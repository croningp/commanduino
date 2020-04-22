"""
.. module:: exceptions
   :platform: Unix
   :synopsis: Holds all the custom exceptions used in Commanduino.
"""


class CMError(Exception):
    """ Base catch-all"""


class CMDeviceRegisterError(CMError):
    """
    When the Bonjour ID is not in the register of the device.
    """
    def __init__(self, bonjour_id):
        self.bonjour_id = bonjour_id

    def __str__(self):
        return '{self.bonjour_id} is not in the register of device'.format(self=self)


class CMCommunicationError(CMError):
    """
    Can't communicate to device - broken connection or device doesn't reply
    """


# CONFIGURATION ERRORS
class CMConfigurationError(CMError):
    """ Base error for wrong configuration """


class CMDeviceConfigurationError(CMConfigurationError):
    """ Bad device config (e.g. missing command_id) """


class CMManagerConfigurationError(CMConfigurationError):
    """Manager can't init due to bad config (e.g. invalid JSON file or missing fields)"""


class CMHandlerConfigurationError(CMConfigurationError):
    """ Handler can't init due to bad config (e.g. specified port cannot be opened) """


class CMTimeout(CMError):
    """All timeout related errors"""


class CMHandlerDiscoveryTimeout(CMTimeout):
    """
    Specified 'io' found but handler not created since no is_init reply was received
    """
    def __init__(self, addr):
        self.addr = addr
        super().__init__()

    def __str__(self):
        return f"Manager at {self.addr} did not initialize.\nCheck that the right port has been used and reset Arduino."


class CMBonjourTimeout(CMTimeout):
    """
    Bonjour device is not available/not found.
    This is always catch and re-raised as CMDeviceDiscoveryTimeout including info on the device generating the error.
    """

    def __init__(self, command_id):
        self.command_id = command_id
        super().__init__()

    def __str__(self):
        return f"{self.command_id} seems to not be existing/available!"


class CMDeviceDiscoveryTimeout(CMError):
    """Specified device not found during bonjour"""


class CMDeviceReplyTimeout(CMTimeout):
    """
    Raised when the device does not respond to a command after a set time frame (default 1 sec).

    Args:
        device_name (str): The name of the device.
        command_name (str): The name of the command.
        elapsed (float): Time elapsed until the exception was thrown.
    """
    def __init__(self, device_name, command_name, elapsed):
        self.device_name = device_name
        self.elapsed = elapsed
        self.command_name = command_name

    def __str__(self):
        return f"{self.device_name} did not respond to {self.command_name} within {self.elapsed:.3} s"
