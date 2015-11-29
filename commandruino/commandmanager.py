from commandhandler import SerialCommandHandler

from lock import Lock

import logging
module_logger = logging.getLogger(__name__)


BONJOUR_REGISTER = {}
from commanddevices.commandservo import CommandServo
BONJOUR_REGISTER['SERVO'] = CommandServo


def create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config):

    if bonjour_id in BONJOUR_REGISTER:
        device = BONJOUR_REGISTER[bonjour_id].from_config(device_config)
        cmdHdl.add_relay(command_id, device.handle_command)
        device.set_command_header(command_id)
        device.set_write_function(cmdHdl.write)
        return device
    else:
        raise DeviceRegisterError(bonjour_id)


class DeviceRegisterError(Exception):
    def __init__(self, bonjour_id):
        self.bonjour_id = bonjour_id

    def __str__(self):
        return '{self.bonjour_id} is not in the register of device'.format(self=self)


class CommandManager(object):

    def __init__(self, serialcommand_configs, devices_dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.serialcommandhandlers = []
        for idx, config in enumerate(serialcommand_configs):
            cmdHdl = SerialCommandHandler.from_config(config)
            cmdHdl.add_default_handler(self.unrecognized)
            cmdHdl.start()
            import time
            time.sleep(1)  # fix this by using a BONJOUR on manager
            self.serialcommandhandlers.append(cmdHdl)

        self.register_all_devices(devices_dict)

    def register_all_devices(self, devices_dict):
        self.devices = {}
        for device_name, device_info in devices_dict.items():
            self.register_device(device_name, device_info)

    def register_device(self, device_name, device_info):
        command_id = device_info['command_id']
        if 'config' in device_info:
            device_config = device_info['config']
        else:
            device_config = {}

        try:
            bojour_service = CommandBonjour(self.serialcommandhandlers)
            cmdHdl, bonjour_id = bojour_service.detect_device(command_id)
            try:
                device = create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config)
                self.devices[device_name] = device
                self.logger.info('Device "{name}" with id "{id}" and of type "{type}" found and registered'.format(name=device_name, id=command_id, type=bonjour_id))
            except DeviceRegisterError:
                self.logger.warning('Device "{name}" of type "{type}" is not in the device register'.format(name=device_name, type=bonjour_id))
        except BonjourError:
            self.logger.warning('Device "{name}" with id "{id}" has not been found'.format(name=device_name, id=command_id))

    @classmethod
    def from_config(cls, config):
        serialcommand_configs = config['ios']
        devices = config['devices']
        return cls(serialcommand_configs, devices)

    @classmethod
    def from_configfile(cls, configfile):
        import json
        with open(configfile) as f:
            return cls.from_config(json.load(f))

    def unrecognized(self, cmd):
        self.logger.warning('Received unknown command "{}"'.format(cmd))


class CommandBonjour(object):

    def __init__(self, serialcommandhandlers):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.serialcommandhandlers = serialcommandhandlers
        self.lock = Lock()
        self.init_bonjour_info()

    def init_bonjour_info(self):
        self.device_bonjour_id = ''
        self.device_bonjour_id_valid = False

    def handle_bonjour(self, *arg):
        if arg[0]:
            self.device_bonjour_id = arg[0]
            self.device_bonjour_id_valid = True
            self.lock.ensure_released()

    def send_bonjour(self, serialcommandhandler, command_id):
        serialcommandhandler.send(command_id, 'BONJOUR')

    def get_bonjour_id(self, serialcommandhandler, command_id):
        self.lock.acquire()
        self.init_bonjour_info()
        self.send_bonjour(serialcommandhandler, command_id)
        is_valid = self.lock.wait_until_released()
        self.lock.ensure_released()
        return self.device_bonjour_id, is_valid

    def detect_device(self, command_id):
        for cmdHdl in self.serialcommandhandlers:
            self.logger.debug('Scanning for "{id}" on port "{port}"...'.format(id=command_id, port=cmdHdl._serial.port))

            cmdHdl.add_relay(command_id, cmdHdl.handle)
            cmdHdl.add_command('BONJOUR', self.handle_bonjour)
            bonjour_id, is_valid = self.get_bonjour_id(cmdHdl, command_id)
            cmdHdl.remove_command('BONJOUR', self.handle_bonjour)
            cmdHdl.remove_relay(command_id, cmdHdl.handle)
            if is_valid:
                return cmdHdl, bonjour_id
        raise BonjourError(command_id)


class BonjourError(Exception):
    def __init__(self, command_id):
        self.command_id = command_id

    def __str__(self):
        return '{self.command_id} seems to not be existing/available'.format(self=self)
