import commanddevice

DEFAULT_REGISTER = commanddevice.BONJOUR_ID
BONJOUR_REGISTER = {}


def add_to_bonjour_register(bonjour_id, constructor):
    BONJOUR_REGISTER[bonjour_id] = constructor


def create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config):

    if bonjour_id in BONJOUR_REGISTER:
        device = BONJOUR_REGISTER[bonjour_id].from_config(device_config)
        cmdHdl.add_relay(command_id, device.handle_command)
        device.set_command_header(command_id)
        device.set_write_function(cmdHdl.write)
        device.init()
        return device
    else:
        raise DeviceRegisterError(bonjour_id)


class DeviceRegisterError(Exception):
    def __init__(self, bonjour_id):
        self.bonjour_id = bonjour_id

    def __str__(self):
        return '{self.bonjour_id} is not in the register of device'.format(self=self)


class DeviceBonjourRegisterError(Exception):
    def __init__(self, command_module_name):
        self.command_module_name = command_module_name

    def __str__(self):
        return '{self.command_module_name} does not contain BONJOUR_ID and CLASS_NAME information'.format(self=self)
