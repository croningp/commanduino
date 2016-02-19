from commandhandler import SerialCommandHandler

from commanddevices.register import create_and_setup_device
from commanddevices.register import DEFAULT_REGISTER
from commanddevices.register import DeviceRegisterError

from lock import Lock

import time
from serial import SerialException

import logging
module_logger = logging.getLogger(__name__)

DEFAULT_INIT_TIMEOUT = 1
DEFAULT_INIT_N_REPEATS = 5

DEFAULT_BONJOUR_TIMEOUT = 0.1

COMMAND_BONJOUR = 'BONJOUR'
COMMAND_IS_INIT = 'ISINIT'
COMMAND_INIT = 'INIT'
COMMAND_RESET = 'RESET'


class CommandManager(object):

    def __init__(self, serialcommand_configs, devices_dict, init_timeout=DEFAULT_INIT_TIMEOUT, init_n_repeats=DEFAULT_INIT_N_REPEATS):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.init_n_repeats = init_n_repeats
        self.init_lock = Lock(init_timeout)

        self.serialcommandhandlers = []
        for idx, config in enumerate(serialcommand_configs):
            try:
                cmdHdl = SerialCommandHandler.from_config(config)
                cmdHdl.add_default_handler(self.unrecognized)
                cmdHdl.start()
            except (SerialException, OSError):
                self.logger.warning('Port {} was not found'.format(config['port']))
                continue
            try:
                elapsed = self.wait_serial_device_for_init(cmdHdl)
                self.logger.info('Found CommandManager on port "{port}", init time was {init_time} seconds'.format(port=cmdHdl._serial.port, init_time=round(elapsed, 3)))
            except InitError:
                self.logger.warning('CommandManager on port "{port}" has not initialized'.format(port=cmdHdl._serial.port))
            self.serialcommandhandlers.append(cmdHdl)

        self.register_all_devices(devices_dict)
        self.set_devices_as_attributes()

    def set_devices_as_attributes(self):
        for device_name, device in self.devices.items():
            if hasattr(self, device_name):
                self.logger.warning("Device named {device_name} is already a reserved attribute, please change name or do not use this pump in attribute mode, rather use pumps[{device_name}]".format(device_name=device_name))
            else:
                setattr(self, device_name, device)

    def handle_init(self, *arg):
        if arg[0] and bool(int(arg[0])):
            self.init_lock.ensure_released()

    def request_init(self, serialcommandhandler):
        serialcommandhandler.send(COMMAND_IS_INIT)

    def request_and_wait_for_init(self, serialcommandhandler):
        start_time = time.time()

        self.init_lock.acquire()
        for i in range(self.init_n_repeats):
            self.request_init(serialcommandhandler)
            is_init, _ = self.init_lock.wait_until_released()
            if is_init:
                break
        self.init_lock.ensure_released()

        elapsed = time.time() - start_time
        return is_init, elapsed

    def wait_serial_device_for_init(self, cmdHdl):
        self.logger.debug('Waiting for init on port "{port}"...'.format(port=cmdHdl._serial.port))

        cmdHdl.add_command(COMMAND_INIT, self.handle_init)
        is_init, elapsed = self.request_and_wait_for_init(cmdHdl)
        cmdHdl.remove_command(COMMAND_INIT, self.handle_init)
        if is_init:
            return elapsed
        raise InitError(cmdHdl._serial.port)

    def send_reset(self, serialcommandhandler):
        serialcommandhandler.send(COMMAND_RESET)

    def reset_and_wait_for_init(self, cmdHdl):
        self.send_reset(cmdHdl)
        self.wait_serial_device_for_init(cmdHdl)

    def reset_all_and_wait_for_init(self):
        for cmdHdl in self.serialcommandhandlers:
            self.send_reset(cmdHdl)
        for cmdHdl in self.serialcommandhandlers:
            self.wait_serial_device_for_init(cmdHdl)

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
            bonjour_service = CommandBonjour(self.serialcommandhandlers)
            cmdHdl, bonjour_id, elapsed = bonjour_service.detect_device(command_id)
            self.logger.info('Device "{name}" with id "{id}" and of type "{type}" found in {bonjour_time}s'.format(name=device_name, id=command_id, type=bonjour_id, bonjour_time=round(elapsed, 3)))
            try:
                device = create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config)
                self.logger.info('Device "{name}" with id "{id}" and of type "{type}" found in the register, creating it'.format(name=device_name, id=command_id, type=bonjour_id, bonjour_time=round(elapsed, 3)))
            except DeviceRegisterError:
                device = create_and_setup_device(cmdHdl, command_id, DEFAULT_REGISTER, device_config)
                self.logger.warning('Device "{name}" with id "{id}" and of type "{type}" is not in the device register, creating a blank minimal device instead'.format(name=device_name, id=command_id, type=bonjour_id))
            self.devices[device_name] = device

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


class InitError(Exception):
    def __init__(self, port):
        self.port = port

    def __str__(self):
        return 'Manager on port {self.port} did not inititalize'.format(self=self)


class CommandBonjour(object):

    def __init__(self, serialcommandhandlers, timeout=DEFAULT_BONJOUR_TIMEOUT):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.serialcommandhandlers = serialcommandhandlers
        self.lock = Lock(timeout)
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
        serialcommandhandler.send(command_id, COMMAND_BONJOUR)

    def get_bonjour_id(self, serialcommandhandler, command_id):
        self.lock.acquire()
        self.init_bonjour_info()
        self.send_bonjour(serialcommandhandler, command_id)
        is_valid, elapsed = self.lock.wait_until_released()
        self.lock.ensure_released()
        return self.device_bonjour_id, is_valid, elapsed

    def detect_device(self, command_id):
        for cmdHdl in self.serialcommandhandlers:
            self.logger.debug('Scanning for "{id}" on port "{port}"...'.format(id=command_id, port=cmdHdl._serial.port))

            cmdHdl.add_relay(command_id, cmdHdl.handle)
            cmdHdl.add_command(COMMAND_BONJOUR, self.handle_bonjour)
            bonjour_id, is_valid, elapsed = self.get_bonjour_id(cmdHdl, command_id)
            cmdHdl.remove_command(COMMAND_BONJOUR, self.handle_bonjour)
            cmdHdl.remove_relay(command_id, cmdHdl.handle)
            if is_valid:
                return cmdHdl, bonjour_id, elapsed
        raise BonjourError(command_id)


class BonjourError(Exception):
    def __init__(self, command_id):
        self.command_id = command_id

    def __str__(self):
        return '{self.command_id} seems to not be existing/available'.format(self=self)
