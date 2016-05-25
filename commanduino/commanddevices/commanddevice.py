from ..commandhandler import CommandHandler
from ..lock import Lock

from .._logger import create_logger

DEFAULT_TIMEOUT = 1

# bonjour info
BONJOUR_ID = 'TEMPLATE'
CLASS_NAME = 'CommandDevice'


class DeviceTimeOutError(Exception):
    def __init__(self, device_name, elapsed):
        self.device_name = device_name
        self.elapsed = elapsed

    def __str__(self):
        return '{device_name} did not respond within {elapsed}s'.format(device_name=self.device_name, elapsed=round(self.elapsed, 3))


class CommandTimeOutError(Exception):
    def __init__(self, device_name, command_name, elapsed):
        self.device_name = device_name
        self.elapsed = elapsed
        self.command_name = command_name

    def __str__(self):
        return '{device_name} did not respond to {command_name} within {elapsed}s'.format(device_name=self.device_name, command_name=self.command_name, elapsed=round(self.elapsed, 3))


class CommandDevice(object):

    def __init__(self):
        self.logger = create_logger(self.__class__.__name__)

        self.cmdHdl = CommandHandler()
        self.cmdHdl.add_default_handler(self.unrecognized)

    def init(self):
        """
        This function is called once the write function is set
        Do your setup here by sending command to the devices
        """
        pass

    @classmethod
    def from_config(cls, config):
        return cls(**config)

    def handle_command(self, cmd):
        self.cmdHdl.handle(cmd)

    def set_command_header(self, cmdHeader):
        self.cmdHdl.set_command_header(cmdHeader)

    def set_write_function(self, write_func):
        self.write = write_func

    def send(self, command_id, *arg):
        self.write(self.cmdHdl.forge_command(command_id, *arg))

    def unrecognized(self, cmd):
        self.logger.warning('Received unknown command "{}"'.format(cmd))

    def register_request(self, request_command, answer_command, variable_name, callback_function_for_variable_update, variable_init_value=None, timeout=DEFAULT_TIMEOUT):

        setattr(self, variable_name, variable_init_value)

        lock_variable_name = variable_name + '_lock'
        setattr(self, lock_variable_name, Lock(timeout))

        self.cmdHdl.add_command(answer_command, callback_function_for_variable_update)

        request_function_name = 'request_' + variable_name

        def request():
            self.send(request_command)

        setattr(self, request_function_name, request)

        get_function_name = 'get_' + variable_name

        def get():
            variable_lock = getattr(self, lock_variable_name)
            variable_lock.acquire()
            getattr(self, request_function_name)()
            is_valid, elapsed = variable_lock.wait_until_released()
            variable_lock.ensure_released()

            if is_valid:
                return getattr(self, variable_name)
            else:
                raise CommandTimeOutError(self.cmdHdl.cmd_header, request_command, elapsed)

        setattr(self, get_function_name, get)
