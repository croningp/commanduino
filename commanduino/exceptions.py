"""
.. module:: exceptions
   :platform: Unix
   :synopsis: Holds all the curstom exceptions used in Commanduino.
"""


class CommanduinoInitError(Exception):
    """
    Raised when the CommandManager handler (either Serial or TCPIP) fails to initialise. Always caught internally.
    """
    def __init__(self, addr):
        self.addr = addr
        super().__init__()

    def __str__(self):
        return f"Manager at {self.addr} did not initialize."


class CommanduinoCommandTimeOutError(Exception):
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
        return '{device_name} did not respond to {command_name} within {elapsed}s'.format(device_name=self.device_name, command_name=self.command_name, elapsed=round(self.elapsed, 3))
