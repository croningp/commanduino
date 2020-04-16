"""

.. module:: commanddevice
   :platform: Unix
   :synopsis: Forms the template of the different Arduino devices.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from ..commandhandler import CommandHandler
from ..lock import Lock
from ..exceptions import CMDeviceReplyTimeout

import logging

# Default timeout value
DEFAULT_TIMEOUT = 1

# Bonjour Information
BONJOUR_ID = 'TEMPLATE'
CLASS_NAME = 'CommandDevice'


class CommandDevice(object):
    """
    Base class to represent the different Arduino devices.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        self.cmdHdl = CommandHandler()
        self.cmdHdl.add_default_handler(self.unrecognized)

    def init(self):
        """
        .. note:: This function is called once the write function is set. Device setup (sending commands) goes here
        """
        pass

    @classmethod
    def from_config(cls, config):
        """
        Obtains the device information from a configuration setup.

        Returns:
            CommandDevice: A new instance of CommandDevice with details set from the configuration.

        """
        return cls(**config)

    def handle_command(self, cmd):
        """
        Handles a command to the device.

        Args:
            cmd (str): The command to handle.

        """
        self.cmdHdl.handle(cmd)

    def set_command_header(self, cmdHeader):
        """
        Sets the command header.

        Args:
            cmdHeader (str): The command header to be set.

        """
        self.cmdHdl.set_command_header(cmdHeader)

    def set_write_function(self, write_func):
        """
        Sets the write function for the device.

        Args:
            write_func (str): The write function to be set.

        """
        self.write = write_func

    def send(self, command_id, *arg):
        """
        Sends a command to/from the device.

        Args:
            command_id (str): The ID of the command.

            *arg: Variable argument.

        """
        self.write(self.cmdHdl.forge_command(command_id, *arg))

    def unrecognized(self, cmd):
        """
        The supplied command is unrecognised.

        Args:
            cmd (str): The supplied command.

        """
        self.logger.warning('Received unknown command "{}"'.format(cmd))

    def register_request(self, request_command, answer_command, variable_name, callback_function_for_variable_update, variable_init_value=None, timeout=DEFAULT_TIMEOUT):
        """
        Registers a new request to/from the device.

        Args:
            request_command (str): The requesting command.

            answer_command (str): The answering command.

            variable_name (str): The name of the variable.

            callback_function_for_variable_update (str): The callback function for updating the variable.

            variable_init_value: Initialisation value for the variable, default set to None.

            timeout (float): Time to wait until timeout, default set to DEFAULT_TIMEOUT (1)

        """

        setattr(self, variable_name, variable_init_value)

        lock_variable_name = variable_name + '_lock'
        setattr(self, lock_variable_name, Lock(timeout))

        self.cmdHdl.add_command(answer_command, callback_function_for_variable_update)

        request_function_name = 'request_' + variable_name

        def request():
            """
            Sends the request command to/from device.
            """
            self.send(request_command)

        setattr(self, request_function_name, request)

        get_function_name = 'get_' + variable_name

        def get():
            """
            Gets the variable name.

            Returns:
                variable_name (str): Name of the variable.

            Raises:
                CommandTimeOutError: Device did not response to command after X time.
            """
            variable_lock = getattr(self, lock_variable_name)
            variable_lock.acquire()
            getattr(self, request_function_name)()
            is_valid, elapsed = variable_lock.wait_until_released()
            variable_lock.ensure_released()

            if is_valid:
                return getattr(self, variable_name)
            else:
                raise CMDeviceReplyTimeout(self.cmdHdl.cmd_header, request_command, elapsed)

        setattr(self, get_function_name, get)
