DEFAULT_REGISTER = 'TEMPLATE'

BONJOUR_REGISTER = {}

from commanddevice import CommandDevice
BONJOUR_REGISTER[DEFAULT_REGISTER] = CommandDevice

from commandservo import CommandServo
BONJOUR_REGISTER['SERVO'] = CommandServo

from commandlinearaccelstepper import CommandLinearAccelStepper
BONJOUR_REGISTER['LINEARACCELSTEPPER'] = CommandLinearAccelStepper


def create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config):

    if bonjour_id in BONJOUR_REGISTER:
        device = BONJOUR_REGISTER[bonjour_id].from_config(device_config)
        cmdHdl.add_relay(command_id, device.handle_command)
        device.set_command_header(command_id)
        device.set_write_function(cmdHdl.write)
        device.init()
    else:
        raise DeviceRegisterError(bonjour_id)
    return device


class DeviceRegisterError(Exception):
    def __init__(self, bonjour_id):
        self.bonjour_id = bonjour_id

    def __str__(self):
        return '{self.bonjour_id} is not in the register of device'.format(self=self)
