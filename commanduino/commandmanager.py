"""
.. module:: commandmanager
   :platform: Unix
   :synopsis: Module to manage various Command Handlers.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from .commandhandler import SerialCommandHandler

from .commanddevices.register import create_and_setup_device
from .commanddevices.register import DEFAULT_REGISTER
from .commanddevices.register import DeviceRegisterError

from .lock import Lock
from ._logger import create_logger

import time
import sys
from serial import SerialException

# Default initialisation timeout
DEFAULT_INIT_TIMEOUT = 1

# Default amount of times to attempt initialisation
DEFAULT_INIT_N_REPEATS = 5

# Default timeout value
DEFAULT_BONJOUR_TIMEOUT = 0.1

COMMAND_BONJOUR = 'BONJOUR'
COMMAND_IS_INIT = 'ISINIT'
COMMAND_INIT = 'INIT'

# removing all stuff related to reset because it does not compile on all boards
# COMMAND_RESET = 'RESET'


class CommandManager(object):
    """
    Manages varying amounts of Command Handler objects.

    Args:
        serialcommand_configs (Tuple): Collection of serial command configurations.

        devices_dict (Dict): Dictionary containing the list of devices.

        init_timeout (int): Initialisation timeout, default se tto DEFAULT_INIT_TIMEOUT (1).

        init_n_repeats (int): Number of times to attempt initialisation, default set to DEFAULT_INIT_N_REPEATS (5).

    Raises:
        OSError: Port was not found.

        SerialException: Port was not found.

        InitError: CommandManager on port was not initialised.
    """
    def __init__(self, serialcommand_configs, devices_dict, init_timeout=DEFAULT_INIT_TIMEOUT, init_n_repeats=DEFAULT_INIT_N_REPEATS):
        self.logger = create_logger(self.__class__.__name__)

        self.initialised = False
        self.init_n_repeats = init_n_repeats
        self.init_lock = Lock(init_timeout)

        self.serialcommandhandlers = []
        for idx, config in enumerate(serialcommand_configs):
            try:
                cmdHdl = SerialCommandHandler.from_config(config)
                cmdHdl.add_default_handler(self.unrecognized)
                cmdHdl.start()
            except (SerialException, OSError):
                if 'required' in config and config['required'] is True:
                    self.logger.error(f"Port {config['port']} was not found and it is required! Aborting...")
                    sys.exit(1)
                else:
                    self.logger.warning(f"Port {config['port']} was not found")
                    continue
            try:
                elapsed = self.wait_serial_device_for_init(cmdHdl)
                self.logger.info('Found CommandManager on port "{port}", init time was {init_time} seconds'.format(port=cmdHdl._serial.port, init_time=round(elapsed, 3)))
            except InitError:
                self.logger.warning('CommandManager on port "{port}" has not initialized'.format(port=cmdHdl._serial.port))
            self.serialcommandhandlers.append(cmdHdl)

        self.register_all_devices(devices_dict)
        self.set_devices_as_attributes()
        self.initialised = True

    def set_devices_as_attributes(self):
        """
        Sets the list of devices as attributes.
        """
        for device_name, device in list(self.devices.items()):
            if hasattr(self, device_name):
                self.logger.warning("Device named {device_name} is already a reserved attribute, please change name or do not use this pump in attribute mode, rather use pumps[{device_name}]".format(device_name=device_name))
            else:
                setattr(self, device_name, device)

    def handle_init(self, *arg):
        """
        Handles the initialisation of the Manager, ensuring that the threading locks are released.

        Args:
            *arg: Variable argument.
        """
        if arg[0] and bool(int(arg[0])):
            self.init_lock.ensure_released()

    def request_init(self, serialcommandhandler):
        """
        Requests initialisation over serial communication.

        Args:
            serialcommandhandler (SerialCommandHandler): Serial Command Handler object for communication.

        """
        serialcommandhandler.send(COMMAND_IS_INIT)

    def request_and_wait_for_init(self, serialcommandhandler):
        """
        Requests initialisation and waits until it obtains a threading lock.

        Args:
            serialcommandhandler (SerialCommandHandler): Serial Command Handler object for communication.

        """
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
        """
        Waits for initialisation using serial communication.

        Args:
            cmdHdl (CommandHandler): CommandHandler object to add/remove commands.

        Returns:
            elapsed (float): Time waited for initialisation.

        Raises:
            InitError: CommandManager on the port was not initialised.

        """
        self.logger.debug('Waiting for init on port "{port}"...'.format(port=cmdHdl._serial.port))

        cmdHdl.add_command(COMMAND_INIT, self.handle_init)
        is_init, elapsed = self.request_and_wait_for_init(cmdHdl)
        cmdHdl.remove_command(COMMAND_INIT, self.handle_init)
        if is_init:
            return elapsed
        raise InitError(cmdHdl._serial.port)

    # removing all stuff related to reset because it does not compile on all boards
    # def send_reset(self, serialcommandhandler):
    #     serialcommandhandler.send(COMMAND_RESET)
    #
    # def reset_and_wait_for_init(self, cmdHdl):
    #     self.send_reset(cmdHdl)
    #     self.wait_serial_device_for_init(cmdHdl)
    #
    # def reset_all_and_wait_for_init(self):
    #     for cmdHdl in self.serialcommandhandlers:
    #         self.send_reset(cmdHdl)
    #     for cmdHdl in self.serialcommandhandlers:
    #         self.wait_serial_device_for_init(cmdHdl)

    def register_all_devices(self, devices_dict):
        """
        Registers all available Arduino devices.

        Args:
            devices_dict (Dict): Dictionary containing all devices.

        """
        self.devices = {}
        for device_name, device_info in list(devices_dict.items()):
            self.register_device(device_name, device_info)

    def register_device(self, device_name, device_info):
        """
        Registers an individual Arduino device.

        Args:
            device_name (str): Name of the device.

            device_info (Dict): Dictionary containing the device information.

        Raises:
            DeviceRegisterError: Device is not in the device register.

            BonjourError: Device has not been found.

        """
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
        """
        Obtains the necessary information from a configuration setup.

        Args:
            cls (CommandManager): The instantiating class.

            config (Dict): Dictionary containing the configuration data.

        """
        serialcommand_configs = config['ios']
        devices = config['devices']
        return cls(serialcommand_configs, devices)

    @classmethod
    def from_configfile(cls, configfile):
        """
        Obtains the configuration data from a configuration file.

        Args:
            cls (CommandManager): The instantiating class.

            configfile (File): The configuration file.

        """
        import json
        with open(configfile) as f:
            return cls.from_config(json.load(f))

    def unrecognized(self, cmd):
        """
        Received command is unrecognised.

        Args:
            cmd (str): The received command.

        """
        # Do not print out unrecognized error during init. as those are "normal" when multiple Arduinos are connected
        if self.initialised:
            self.logger.warning('Received unknown command "{}"'.format(cmd))


class VirtualCommandManager(CommandManager):
    def __init__(self, serialcommand_configs, devices_dict, init_timeout=DEFAULT_INIT_TIMEOUT, init_n_repeats=DEFAULT_INIT_N_REPEATS):
        self.logger = create_logger(self.__class__.__name__)

        self.init_n_repeats = init_n_repeats
        self.init_lock = Lock(init_timeout)

        self.serialcommandhandlers = []
        self.initialised = True
        self.register_all_devices(devices_dict)
        self.set_devices_as_attributes()
        self.initialised = True

    def register_device(self, device_name, device_info):
        """
        Registers an individual Arduino device.

        Args:
            device_name (str): Name of the device.

            device_info (Dict): Dictionary containing the device information.

        Raises:
            DeviceRegisterError: Device is not in the device register.

            BonjourError: Device has not been found.

        """
        command_id = device_info['command_id']
        if 'config' in device_info:
            device_config = device_info['config']
        else:
            device_config = {}

        from commanduino.commanddevices import CommandVirtual

        self.devices[device_name] = CommandVirtual()


class InitError(Exception):
    """
    Exception for when the manager fails to initialise.
    """
    def __init__(self, port):
        self.port = port

    def __str__(self):
        return 'Manager on port {self.port} did not initialize'.format(self=self)


class CommandBonjour(object):
    """
    Represents a Command Manager for Bonjour devices.

    Args:
        serialcommandhandlers: Collection of SerialCommandHandler objects.

        timeout (float): Time to wait before timeout, default set to DEFAULT_BONJOUR_TIMEOUT (0.1)

    """
    def __init__(self, serialcommandhandlers, timeout=DEFAULT_BONJOUR_TIMEOUT):
        self.logger = create_logger(self.__class__.__name__)

        self.serialcommandhandlers = serialcommandhandlers
        self.lock = Lock(timeout)
        self.init_bonjour_info()

    def init_bonjour_info(self):
        """
        Initialises the Bonjour information.
        """
        self.device_bonjour_id = ''
        self.device_bonjour_id_valid = False

    def handle_bonjour(self, *arg):
        """
        Handles the Bonjour initialisation.

        Args:
            *arg: Variable argument.
        """
        if arg[0]:
            self.device_bonjour_id = arg[0]
            self.device_bonjour_id_valid = True
            self.lock.ensure_released()

    def send_bonjour(self, serialcommandhandler, command_id):
        """
        Sends a message to the device.

        .. todo:: Fix this up

        Args:
            serialcommandhandler (SerialCommandHandler): The Serial Command Handler object.

            command_id (str): The ID of the command.

        """
        serialcommandhandler.send(command_id, COMMAND_BONJOUR)

    def get_bonjour_id(self, serialcommandhandler, command_id):
        """
        Obtains the device's bonjour ID.

        Args:
            serialcommandhandler (SerialCommandHandler): The Serial Command Handler object.

            command_id (str): The ID of the command.

        Returns:
            self.device_bonjour_id (str): The Bonjour ID.

            is_valid (bool): Validity of the ID.

            elapsed (float): Time elapsed since request.

        """
        self.lock.acquire()
        self.init_bonjour_info()
        self.send_bonjour(serialcommandhandler, command_id)
        is_valid, elapsed = self.lock.wait_until_released()
        self.lock.ensure_released()
        return self.device_bonjour_id, is_valid, elapsed

    def detect_device(self, command_id):
        """
        Attempts to detect the Bonjour device.

        Args:
            command_id (str): The ID of the command.

        Returns:
            cmdHdl (SerialCommandHandler): The Serial Command Handler.

            bonjour_id (str): The Bonjour ID.

            elapsed (float): Time elapsed since request.

        """
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
    """
    Exception for when Bonjour device is not available/not found.
    """
    def __init__(self, command_id):
        self.command_id = command_id

    def __str__(self):
        return '{self.command_id} seems to not be existing/available'.format(self=self)
