"""
.. module:: commandmanager
   :platform: Unix
   :synopsis: Module to manage various Command Handlers.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from .commandhandler import SerialCommandHandler
from .commandhandler import TCPIPCommandHandler

from .commanddevices.register import create_and_setup_device
from .commanddevices.register import DEFAULT_REGISTER

from .exceptions import (CMManagerConfigurationError,
                         CMHandlerConfigurationError,
                         CMHandlerDiscoveryTimeout,
                         CMDeviceConfigurationError,
                         CMBonjourTimeout,
                         CMDeviceDiscoveryTimeout,
                         CMDeviceRegisterError,
                         CMCommunicationError)

from .lock import Lock

from .commanddevices import CommandDevice

import time
import json
import logging
from typing import Optional, Any

from typing import Dict, List, Tuple
from commanduino.commandhandler import GenericCommandHandler

# Default initialisation timeout
DEFAULT_INIT_TIMEOUT = 1

# Default amount of times to attempt initialisation
DEFAULT_INIT_N_REPEATS = 5

# Default timeout value
DEFAULT_BONJOUR_TIMEOUT = 0.1

COMMAND_BONJOUR = 'BONJOUR'
COMMAND_IS_INIT = 'ISINIT'
COMMAND_INIT = 'INIT'


class CommandManager(object):
    """
    Manages varying amounts of Command Handler objects.

    Args:
        command_configs: Collection of command configurations.

        devices_dict: Dictionary containing the list of devices.

        init_timeout: Initialisation timeout, default set to DEFAULT_INIT_TIMEOUT (1).

        init_n_repeats: Number of times to attempt initialisation, default set to DEFAULT_INIT_N_REPEATS (5).
    """
    def __init__(self, command_configs: List[Dict], devices_dict: Dict, init_timeout: float = DEFAULT_INIT_TIMEOUT,
                 init_n_repeats: int = DEFAULT_INIT_N_REPEATS, simulation: bool = False):
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        self._simulation = simulation

        self.initialised = False
        self.init_n_repeats = init_n_repeats
        self.init_lock = Lock(init_timeout)

        self.commandhandlers: List[GenericCommandHandler] = []
        if not self._simulation:
            for config_entry in command_configs:
                # Create handler from config & initialize device
                self.add_command_handler(config_entry)
        else:
            self.logger.info("Simulation mode, skipping handlers creation.")
            self.commandhandlers = command_configs  # type: ignore

        self.devices: Dict[str, Any] = {}
        self.register_all_devices(devices_dict)
        self.set_devices_as_attributes()
        self.initialised = True

    def add_command_handler(self, handler_config: Dict) -> None:
        """Creates command handler from the configuration dictionary, tests connection
        and appends instance to self.commandhandlers

        Args:
            handler_config: Handler configuration dictionary.
        """
        if self._simulation:
            self.logger.info("Simulation mode, skipping handlers addition.")
            self.commandhandlers.append(handler_config)  # type: ignore
            return None
        # Make a copy not to mutate original dict - might be re-used
        # by upper-level code for object re-creation.
        handler_config = handler_config.copy()
        # Check if type is present, if not - log and fall back to serial
        # for backwards compatibility reasons.
        if "type" in handler_config:
            handler_type = handler_config["type"]
            # Remove connection type from config dict copy - not needed any more
            handler_config.pop("type")
        else:
            self.logger.warning("No command handler type provided in configuration. Falling back to serial.")
            handler_type = "serial"
        # Get full name - for use in logging
        device_name = handler_config.get("address", "") + ":" + handler_config.get("port", "")
        # Check if handler is required & remove the key from dict
        required = handler_config.get("required", False)
        handler_config.pop("required", None)

        try:
            if handler_type == "serial":
                handler = SerialCommandHandler.from_config(handler_config)
                self.logger.info("Created serial-based command handler for %s.", device_name)
            elif handler_type == "tcpip":
                handler = TCPIPCommandHandler.from_config(handler_config)
                self.logger.info("Created socket-based command handler for %s.", device_name)
        except CMHandlerConfigurationError as e:
            if required:
                raise CMHandlerConfigurationError(f"Error initializing device {device_name}: {e}") from None
            else:
                self.logger.warning(f"I/O device {device_name} (type {handler_type}) was not found")
                self.logger.warning("Additional error message: %s", e)
        else:
            # If CommandHandler creation succeeded, add callback, start handler and initialize it
            assert isinstance(handler, (SerialCommandHandler, TCPIPCommandHandler))
            handler.add_default_handler(self.unrecognized)
            handler.start()
            try:
                elapsed = self.wait_device_for_init(handler)
                self.logger.info(f"Found Arduino CommandManager at {device_name}, init time was {elapsed:.3} seconds")
            except CMHandlerDiscoveryTimeout:
                self.logger.warning(f"Arduino CommandManager at {device_name} has not initialized")
            else:
                # Update handlers list
                self.commandhandlers.append(handler)

    def remove_command_handler(self, handler_to_remove: GenericCommandHandler) -> None:
        """
        Deletes the command handler object & removes a reference to it from
        class dictionary. Then deletes the devices bound to the handler being deleted.

        The method to detect which devices depend on the handler being deleted
        may seem wanky because it is.
        However, it is the only possible method as every device internal
        CommandHandler doesn't hold a reference to an actual command handler.
        The only thing having this reference is the device's write() function
        which gets updated on create_and_setup_device()
        """
        if self._simulation:
            self.logger.info("Simulation mode, skipping handlers removal.")
            return None
        if handler_to_remove not in self.commandhandlers:
            self.logger.warning("Command handler %s not found!", handler_to_remove)
            return
        self.logger.info("Removing devices...")
        # Find the dependent devices to remove (i.e. the devices using that handler)
        for name, dev in self.devices.copy().items():
            # write.__self__ is the CommandHandler instance owning the write function set to CommandDevice.write
            if handler_to_remove is dev.write.__self__:  # type: ignore
                self.logger.info("Removing dependent device %s", name)
                self.unregister_device(name)
        # Remove handler
        self.logger.info("Removing command handler...")
        self.commandhandlers.remove(handler_to_remove)

    def set_devices_as_attributes(self) -> None:
        """
        Sets the list of devices as attributes.
        """
        for device_name, device in list(self.devices.items()):
            if hasattr(self, device_name):
                self.logger.warning(f"Device named {device_name} is already a reserved attribute! "
                                    f"Please change name or do not use this device in attribute mode, "
                                    f"rather use devices[{device_name}]")
            else:
                setattr(self, device_name, device)

    def handle_init(self, *arg) -> None:
        """
        Handles the initialisation of the Manager, ensuring that the threading locks are released.

        Args:
            *arg: Variable argument.
        """
        if arg[0] and bool(int(arg[0])):
            self.init_lock.ensure_released()

    def request_init(self, handler: GenericCommandHandler) -> None:
        """
        Requests initialisation over communication link.

        Args:
            handler: Command Handler object for communication.

        """
        handler.send(COMMAND_IS_INIT)

    def request_and_wait_for_init(self, handler: GenericCommandHandler) -> Tuple[bool, float]:
        """
        Requests initialisation and waits until it obtains a threading lock.

        Args:
            handler: Command Handler object for communication.

        """
        start_time = time.time()

        self.init_lock.acquire()
        for _ in range(self.init_n_repeats):
            self.request_init(handler)
            is_init, _ = self.init_lock.wait_until_released()
            if is_init:
                break
        self.init_lock.ensure_released()

        elapsed = time.time() - start_time
        return is_init, elapsed

    def wait_device_for_init(self, handler: GenericCommandHandler) -> float:
        """
        Waits for initialisation using communication link.

        Args:
            handler: Command Handler object to add/remove commands.

        Returns:
            elapsed: Time waited for initialisation.

        Raises:
            CMHandlerDiscoveryTimeout: CommandManager on the port was not initialised.

        """
        self.logger.debug('Waiting for device at %s to init...', handler.name)

        handler.add_command(COMMAND_INIT, self.handle_init)
        try:
            is_init, elapsed = self.request_and_wait_for_init(handler)
        except CMCommunicationError:
            raise CMHandlerDiscoveryTimeout(handler.name)
        handler.remove_command(COMMAND_INIT, self.handle_init)
        if is_init:
            return elapsed
        raise CMHandlerDiscoveryTimeout(handler.name)

    def register_all_devices(self, devices_dict: Dict) -> None:
        """
        Registers all available Arduino devices.

        Args:
            devices_dict: Dictionary containing all devices.

        """
        for device_name, device_info in devices_dict.items():
            try:
                self.register_device(device_name, device_info)
            except CMDeviceConfigurationError as e:
                self.logger.error(e)

    def register_device(self, device_name: str, device_info: Dict) -> None:
        """
        Registers an individual Arduino device.

        Args:
            device_name: Name of the device.

            device_info: Dictionary containing the device information.

        Raises:
            CMDeviceRegisterError: Device is not in the device register.

            CMBonjourError: Device has not been found.

        """

        # Command ID must contain a valid string
        command_id = device_info.get('command_id', "")
        if command_id == "":
            raise CMDeviceConfigurationError(f"Invalid or missing 'command_id' in {device_name} configuration!")

        # Configuration is optional
        device_config = device_info.get("config", {})

        if not self._simulation:
            # Look for device via bonjour on all handlers
            try:
                bonjour_service = CommandBonjour(self.commandhandlers)
                handler, bonjour_id, elapsed = bonjour_service.detect_device(command_id)
                self.logger.debug(f"Device '{device_name}' (ID=<{command_id}> type=<{bonjour_id}>) found on {handler.name}")
            except CMBonjourTimeout:
                raise CMDeviceDiscoveryTimeout(f"Device '{device_name}' (ID=<{command_id}>) has not been found!") from None

            # Initialise device
            try:
                device = create_and_setup_device(handler, command_id, bonjour_id, device_config)
                self.logger.debug(f"Device '{device_name}' created! (ID=<{command_id}> type=<{bonjour_id}> handler="
                                 f"<{handler.name}> detection time {elapsed:.3f} s)")
            except CMDeviceRegisterError:
                device = create_and_setup_device(handler, command_id, DEFAULT_REGISTER, device_config)
                self.logger.warning(f"Device '{device_name}' NOT found in the register! Initialized as blank minimal object"
                                    f"! (ID=<{command_id}> type=<{bonjour_id}> handler=<{handler.name}>)")
            self.devices[device_name] = device
        else:
            device = VirtualDevice(device_name, device_config)
            self.devices[device_name] = device

    def unregister_device(self, device_name: str) -> None:
        """
        Removes device attribute & reference from devices dictionary
        """
        # Remove device attribute from self
        delattr(self, device_name)
        # Remove reference from device list
        self.devices.pop(device_name)

    @classmethod
    def from_config(cls, config) -> 'CommandManager':
        """
        Obtains the necessary information from a configuration setup.

        Args:
            cls (CommandManager): The instantiating class.

            config (Dict): Dictionary containing the configuration data.

        """
        try:
            command_configs = config["ios"]
            devices = config["devices"]
        except KeyError as e:
            raise CMManagerConfigurationError(f"Invalid configuration provided: missing {e} in dict!") from None
        sim = config.get("simulation", False)
        return cls(command_configs, devices, simulation=sim)

    @classmethod
    def from_configfile(cls, configfile: str, simulation: Optional[bool] = None) -> 'CommandManager':
        """
        Obtains the configuration data from a configuration file.

        Args:
            cls (CommandManager): The instantiating class.

            configfile (File): The configuration file.

            simulation (bool): True if simulation mode is needed.

        """
        try:
            with open(configfile) as f:
                config_dict = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            # Printing "e" as well as it holds info on the line/column where the error occurred
            raise CMManagerConfigurationError(f"The JSON file provided {configfile} is invalid!\n{e}") from None
        # Parameter overrides config file only if provided
        if simulation is not None:
            config_dict["simulation"] = simulation
        return cls.from_config(config_dict)

    def unrecognized(self, cmd: str) -> None:
        """
        Received command is unrecognised.

        Args:
            cmd (str): The received command.

        """
        # Do not print out unrecognized error during init. as those are "normal" when multiple Arduinos are connected
        if self.initialised:
            self.logger.warning('Received unknown command "{}"'.format(cmd))


class CommandBonjour(object):
    """
    Represents a Command Manager for Bonjour devices.

    Args:
        commandhandlers: Collection of CommandHandler objects.

        timeout: Time to wait before timeout, default set to DEFAULT_BONJOUR_TIMEOUT (0.1)

    """
    def __init__(self, commandhandlers: List[GenericCommandHandler],
                 timeout: float = DEFAULT_BONJOUR_TIMEOUT):
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        self.commandhandlers = commandhandlers
        self.lock = Lock(timeout)
        # Init bonjour info
        self.device_bonjour_id = ''
        self.device_bonjour_id_valid = False

    def clear_bonjour_info(self) -> None:
        """
        Initialises the Bonjour information.
        """
        self.device_bonjour_id = ''
        self.device_bonjour_id_valid = False

    def handle_bonjour(self, *arg) -> None:
        """
        Handles the Bonjour initialisation.

        Args:
            *arg: Variable argument.
        """
        if arg[0]:
            self.device_bonjour_id = arg[0]
            self.device_bonjour_id_valid = True
            self.lock.ensure_released()

    def send_bonjour(self, handler: GenericCommandHandler, command_id: str) -> None:
        """
        Sends a message to the device.

        .. todo:: Fix this up

        Args:
            handler: The Command Handler object.

            command_id: The ID of the command.

        """
        handler.send(command_id, COMMAND_BONJOUR)

    def get_bonjour_id(self, handler: GenericCommandHandler, command_id: str) -> Tuple[str, bool, float]:
        """
        Obtains the device's bonjour ID.

        Args:
            handler: The Command Handler object.

            command_id: The ID of the command.

        Returns:
            self.device_bonjour_id: The Bonjour ID.

            is_valid: Validity of the ID.

            elapsed: Time elapsed since request.

        """
        self.lock.acquire()
        self.clear_bonjour_info()
        self.send_bonjour(handler, command_id)
        is_valid, elapsed = self.lock.wait_until_released()
        self.lock.ensure_released()
        return self.device_bonjour_id, is_valid, elapsed

    def detect_device(self, command_id: str) -> Tuple[GenericCommandHandler, str, float]:
        """
        Attempts to detect the Bonjour device.

        Args:
            command_id: The ID of the command.

        Returns:
            handler: TheCommand Handler object.

            bonjour_id: The Bonjour ID.

            elapsed: Time elapsed since request.

        """
        for handler in self.commandhandlers:
            self.logger.debug('Scanning for "%s" at "%s"...', command_id, handler.name)

            handler.add_relay(command_id, handler.handle)
            handler.add_command(COMMAND_BONJOUR, self.handle_bonjour)
            bonjour_id, is_valid, elapsed = self.get_bonjour_id(handler, command_id)
            handler.remove_command(COMMAND_BONJOUR, self.handle_bonjour)
            handler.remove_relay(command_id, handler.handle)
            if is_valid:
                return handler, bonjour_id, elapsed
        raise CMBonjourTimeout(command_id)


class VirtualAttribute:
    """ Callable attribute for virtual device
    """
    def __call__(self, *args, **kwargs):
        # Make nice arguments string for logging
        args = ", ".join([str(arg) for arg in args])
        if args and kwargs:
            args += ","
        kwargs = ", ".join([str(k)+"="+str(v) for k, v in kwargs.items()])
        self.logger.info("Virtual call %s(%s%s)", self.name, args, kwargs)

    def __init__(self, name, logger):
        self.name = name
        self.logger = logger
        self.logger.info("Created virtual method %s()", name)


class VirtualDevice:
    """ Virtual device mock to replace normal devices in simulation mode
    """
    def __getattr__(self, name):

        # Check if we already have this attribute defined,
        # e.g. from device_config during __init__()
        # or previous __setattr__() calls
        if name in self.__dict__:
            return self.__dict__[name]
        # Otherwise create a virtual callable
        self.__dict__[name] = VirtualAttribute(name, self.__dict__["logger"])
        return self.__dict__[name]

    def __setattr__(self, name, value):

        # Check if we already have this attribute defined,
        # e.g. from device_config during __init__()
        # or previous __setattr__() calls
        if name not in self.__dict__:
            self.__dict__["logger"].debug("Creating virtual attribute %s=%s", name, value)
        elif callable(self.__dict__[name]):
            self.logger.warning("Redefining virtual method %s with virtual attribute", self.__dict__[name])

        self.__dict__[name] = value

    def __init__(self, name=None, device_info = None):

        # Setup logger
        self.__dict__["logger"] = logging.getLogger(__name__).getChild(self.__class__.__name__)

        # Populate device configuration, if present
        # These are static non-callable attributes
        if device_info is not None:
            for k, v in device_info.items():
                self.__dict__[k] = v
        self.__dict__["logger"].info("Created virtual device %s", name)
