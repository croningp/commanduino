"""

.. module:: register
   :platform: Unix
   :synopsis: This module is used to register the different kinds of devices.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

from . import commanddevice

DEFAULT_REGISTER = commanddevice.BONJOUR_ID
BONJOUR_REGISTER = {}


def add_to_bonjour_register(bonjour_id, constructor):
    """
    Adds the device to the Bonjour register.

    Args:
        bonjour_id (str): The Bonjour ID.

        constructor: The constructor for registration.

    """
    BONJOUR_REGISTER[bonjour_id] = constructor


def create_and_setup_device(cmdHdl, command_id, bonjour_id, device_config):
    """
    Creates and sets up the Arduino device for usage.

    Args:
        cmdHdl (SerialCommandHandler): The Serial Command Handler object for serial communication.

        command_id (str): The ID of the command.

        bonjour_id (str): The Bonjour ID.

        device_config (Dict): Dictionary containing the device configuration.

    Raises:
        DeviceRegisterError: Bonjour ID is not in the register of the device.

    """
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
    """
    Exception for handling when the Bonjour ID is not in the register of the device.
    """
    def __init__(self, bonjour_id):
        self.bonjour_id = bonjour_id

    def __str__(self):
        return '{self.bonjour_id} is not in the register of device'.format(self=self)


class DeviceBonjourRegisterError(Exception):
    """
    Exception for handling when the Arduino device does not contain Bonjour ID and Class Name information.
    """
    def __init__(self, command_module_name):
        self.command_module_name = command_module_name

    def __str__(self):
        return '{self.command_module_name} does not contain BONJOUR_ID and CLASS_NAME information'.format(self=self)
