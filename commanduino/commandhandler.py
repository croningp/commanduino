"""

.. module:: commandhandler
   :platform: Unix
   :synopsis: Handles the communication to/from the Arduino Hardware.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
import time
import serial
import socket
import threading
import logging
from typing import Callable, Dict, List, Union

from .exceptions import CMHandlerConfigurationError, CMTimeout, CMCommunicationError

# Default delimiter to separate commands
DEFAULT_DELIM = ','

# Default terminal character of a command
DEFAULT_TERM = ';'

# Default decimal
DEFAULT_CMD_DECIMAL = 2

# Default baudrate for communication
DEFAULT_BAUDRATE = 115200

# Default timeout time
DEFAULT_TIMEOUT = 0.01


class CommandHandler(object):
    """
    Represents the Command Handler which will handle commands to/from the Arduino hardware.

    Args:
        delim: Delimiter of the command, default set to DEFAULT_DELIM(',')

        term: Terminal character of the command, set to DEFAULT_TERM(';')

        cmd_decimal: Decimal of the command, default set to DEFAULT_CMD_DECIMAL(2)

    """

    @classmethod
    def from_config(cls, config: Dict) -> 'CommandHandler':
        """
        Obtains the details of the handler from a configuration.

        Args:
            cls: The instantiating class.

            config: Dictionary containing the configuration details.

        Returns:
            CommandHandler: New CommandHandler object with details set from a configuration setup.

        """
        return cls(**config)

    def __init__(self, delim: str = DEFAULT_DELIM, term: str = DEFAULT_TERM, cmd_decimal: int = DEFAULT_CMD_DECIMAL,
                 **kwargs):
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        # Something descriptive to reference the handler in logs.
        self.name = self.__class__.__name__

        self.delim = delim  # character separating args in a message
        self.term = term  # character ending a message

        self.buffer = ''  # string that will hold the received data

        self.handlers: Dict[str, List[Callable]] = {}
        self.relays: Dict[str, List[Callable]] = {}
        self.default_handlers: List[Callable] = []

        self.cmd_header = ''
        self.cmd_decimal = cmd_decimal

    def process_char(self, a_char: bytes) -> None:
        """
        Processes a single character of a command and adds it to the receiving buffer.
        If the terminator character is found, process the buffer.

        Args:
            a_char: The character to be processed

        """
        if a_char:
            decoded_char = a_char.decode(encoding="utf-8", errors="ignore")
            if decoded_char == self.term:
                self.handle(self.buffer)
                self.buffer = ''
            else:
                self.buffer += decoded_char

    def handle(self, cmd: str):
        """
        Handles a full command to/from the Arduino hardware.

        Args:
            cmd: The command to be handled.

        """
        cmd = cmd.strip().strip(self.term)
        cmd_list = cmd.split(self.delim)
        cmd_id = cmd_list[0]

        self.logger.debug('Handling "{}"'.format(cmd),
                          extra={'cmd_list': cmd_list,
                                 'cmd_id': cmd_id})

        if cmd_id in self.handlers:
            for clb in self.handlers[cmd_id]:
                self.logger.debug('Found callback for "{}"'.format(cmd_id),
                                  extra={'callback_function': clb})
                clb(*cmd_list[1:])  # all args in the command are given to the callback function as arguments
        elif cmd_id in self.relays:
            for clb in self.relays[cmd_id]:
                self.logger.debug('Found relay for "{}"'.format(cmd_id),
                                  extra={'relay_function': clb})
                clb(self.build_remaining(cmd_list))
        else:
            self.logger.debug('No callback assigned to "{}", defaulting'.format(cmd_id))
            for clb in self.default_handlers:
                clb(cmd)  # give back what was received

    def build_remaining(self, cmd_list: List[str]) -> str:
        """
        Builds an Arduino command from a list of partial commands.

        Args:
            cmd_list: The list of command constituents.

        """
        return self.delim.join(cmd_list[1:]) + self.term

    def add_command(self, command_id: str, callback_function: Callable) -> None:
        """
        Adds an Arduino command to the handler.

        Args:
            command_id: The ID of the command.

            callback_function: A copy of the command to "callback".

        """
        if command_id not in self.handlers:
            self.handlers[command_id] = []
        if callback_function not in self.handlers[command_id]:
            self.handlers[command_id].append(callback_function)

    def remove_command(self, command_id: str, callback_function: Callable) -> None:
        """
        Removes an Arduino command from the Handler.

        Args:
            command_id: The ID of the command.

            callback_function: A copy of the command to "callback".

        """
        if command_id in self.handlers:
            if callback_function in self.handlers[command_id]:
                self.handlers[command_id].remove(callback_function)

    def add_relay(self, command_id: str, callback_function: Callable) -> None:
        """
        Adds a relay to the Handler.

        Args:
            command_id: The ID of the command.

            callback_function: A copy of the command to "callback".

        """
        if command_id not in self.relays:
            self.relays[command_id] = []
        if callback_function not in self.relays[command_id]:
            self.relays[command_id].append(callback_function)

    def remove_relay(self, command_id: str, callback_function: Callable) -> None:
        """
        Removes a relay form the Handler.

        Args:
            command_id: The ID of the command.

            callback_function: A copy of the command to "callback".

        """
        if command_id in self.relays:
            if callback_function in self.relays[command_id]:
                self.relays[command_id].remove(callback_function)

    def add_default_handler(self, callback_function: Callable) -> None:
        """
        Adds a default handler to the device.

        Args:
            callback_function: A copy of the command to "callback".

        """
        if callback_function not in self.default_handlers:
            self.default_handlers.append(callback_function)

    def remove_default_handler(self, callback_function: Callable) -> None:
        """
        Removes a default handler from the device.

        Args:
            callback_function: A copy of the command to "callback".

        """
        if callback_function in self.default_handlers:
            self.default_handlers.remove(callback_function)

    #
    def set_command_header(self, cmd_header: str, add_delim: bool = True) -> None:
        """
        Sets the header of the Arduino command.

        Args:
            cmd_header: The header of the command.

            add_delim: Adds a delimiter to the command, default set to True.

        """
        self.cmd_header = cmd_header
        if add_delim:
            self.cmd_header += self.delim
        self.logger.debug('Set command header to "{}"'.format(self.cmd_header))

    def set_command_decimal(self, cmd_decimal: int) -> None:
        """
        Sets the decimal of the Arduino command.

        Args:
            cmd_decimal: The decimal of the command.

        """
        self.cmd_decimal = cmd_decimal
        self.logger.debug('Set decimal to "{}"'.format(self.cmd_decimal))

    def forge_command(self, command_id: str, *args) -> str:
        """
        Creates a full Arduino command.

        Args:
            command_id: The ID of the command.

            *args: Variable length argument list.

        """
        cmd = self.cmd_header
        cmd += command_id
        for arg in args:
            cmd += self.delim
            if type(arg) == float:
                cmd += str(round(arg, self.cmd_decimal))
            else:
                cmd += str(arg)
        cmd += self.term

        self.logger.debug('Forged "{}"'.format(cmd),
                          extra={'command_id': command_id,
                                 'arguments': args})

        return cmd


class SerialCommandHandler(threading.Thread, CommandHandler):
    """
    Represents the Command Handler which will handle commands to/from the Arduino hardware via Serial Communication.

    Args:
        port: The port to communicate over.

        baudrate: The baudrate of the serial communication, default set to DEFAULT_BAUDRATE (115200)

        timeout: The time to wait for timeout, default set to DEFAULT_TIMEOUT (0.01)

        delim: The delimiting character of a command, default set to DEFAULT_DELIM (',')

        term: The terminal character of a command, default set to DEFAULT_TERM (';')

        cmd_decimal: The decimal of the command, default set to DEFAULT_CMD_DECIMAL (2)

    """
    def __init__(self, port: str, baudrate: int = DEFAULT_BAUDRATE, timeout: float = DEFAULT_TIMEOUT,
                 delim: str = DEFAULT_DELIM, term: str = DEFAULT_TERM, cmd_decimal: int = DEFAULT_CMD_DECIMAL):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        CommandHandler.__init__(self, delim, term, cmd_decimal)
        self.name = port
        self.open(port, baudrate, timeout)

    def open(self, port: str, baudrate: int, timeout: float) -> None:
        """
        Opens the serial communication between the PC and Arduino board.

        Args:
            port: The port to communicate over.

            baudrate: The baudrate of serial communication.

            timeout: The time to wait for timeout.

        """
        self.logger.debug('Opening port {}'.format(port),
                          extra={'port': port,
                                 'baudrate': baudrate,
                                 'timeout': timeout})
        try:
            self._serial = serial.Serial(port, baudrate, timeout=timeout)
        except (serial.SerialException, TypeError, ValueError) as e:
            raise CMHandlerConfigurationError(str(e))

    def close(self) -> None:
        """
        Closes the serial communication between the PC and Arduino board.
        """
        if hasattr(self, "_serial"):
            self._serial.close()
            self.logger.debug('Closing port "{}"'.format(self._serial.port))

    def __del__(self):
        """
        Closes the serial communication between the PC and Arduino board.
        """
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the serial communication between the PC and Arduino Board, due to an exception occurrence.

        Args:
            exc_type (str): The exception type.

            exc_value: The value of the exception.

            traceback (str): The position in the code where the exception occurred.

        """
        self.close()

    def stop(self) -> None:
        """
        Releases the lock when signalled via an interrupt.
        """
        self.interrupted.release()

    def run(self) -> None:
        """
        Starts the Handler processing commands.
        """
        self.interrupted.acquire()
        while self.interrupted.locked():
            try:
                self.process_serial(self._serial)
            except (serial.SerialException, serial.SerialTimeoutException) as e:
                raise CMTimeout(f"Error reading from serial port {self._serial.port}! {e}") from None
        self.close()

    def send(self, command_id: str, *arg) -> None:
        """
        Sends a command over the serial communication.

        Args:
            command_id (str): The ID of the command.

            *arg: Variable argument.

        """
        self.write(self.forge_command(command_id, *arg))

    def write(self, msg: str) -> None:
        """
        Writes a message over the serial communication.

        Args:
            msg (str): The message to send.

        """
        self.logger.debug('Sending "{}" on port "{}"'.format(msg, self._serial.port))
        try:
            self._serial.write(msg.encode())
        except serial.SerialException as e:
            raise CMCommunicationError(f"Error writing to serial port {self._serial.port}! {e}") from None

    def process_serial(self, a_serial: serial.Serial) -> None:
        """
        Processes the serial communication to obtain data to be processed.

        Args:
            a_serial: The serial to read from.

        """
        self.process_char(a_serial.read(1))

    def wait_until_running(self, sleep_time: float = 0.01) -> None:
        """
        Waits until the current thread is running.

        Args:
            sleep_time (float): The time to wait for, default set to 0.01

        """
        while not self.interrupted.locked():
            time.sleep(sleep_time)


class TCPIPCommandHandler(threading.Thread, CommandHandler):
    """
    Represents the Command Handler which will handle commands to/from the Arduino hardware via TCP/IP socket.

    Args:
        port: The TCP/UDP port to communicate over.

        address: The IP address of the device.

        protocol: Either tcp or udp, default set to TCP.

        timeout: The time to wait for timeout, default set to DEFAULT_TIMEOUT (0.01)

        delim: The delimiting character of a command, default set to DEFAULT_DELIM (',')

        term: The terminal character of a command, default set to DEFAULT_TERM (';')

        cmd_decimal: The decimal of the command, default set to DEFAULT_CMD_DECIMAL (2)

    """
    def __init__(self, port: str, address: str, protocol: str = "TCP", timeout: float = DEFAULT_TIMEOUT,
                 delim: str = DEFAULT_DELIM, term: str = DEFAULT_TERM, cmd_decimal: int = DEFAULT_CMD_DECIMAL):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Event()
        self.interrupted.clear()

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

        CommandHandler.__init__(self, delim, term, cmd_decimal)

        self.name = address + ":" + port

        self._connection: socket.socket = None  # type: ignore

        self.open(port, address, protocol.upper(), timeout)

    def open(self, port: str, address: str, protocol: str, timeout: float):
        """
        Opens the TCP/IP communication between the PC and Arduino board.

        Args:
            port: The port to communicate over.

            address: The IP address of the device.

            protocol: Protocol to use - TCP or UDP

            timeout: The time to wait for timeout.

        """
        self.logger.debug('Opening connection to %s:%s (%s)', address, port, protocol)

        try:
            if protocol == "TCP":
                self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif protocol == "UDP":
                self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                raise CMHandlerConfigurationError(f"Unknown transport layer protocol <{protocol}> provided!")
            self._connection.connect((address, int(port)))
            # Receive timeout in seconds.
            # This has to be done after opening the connection to avoid connect() error on non-blocking socket
            self._connection.settimeout(timeout)
        except TimeoutError as e:
            raise CMHandlerConfigurationError(f"Socket timeout! {e}")
        except (OSError, TypeError, ValueError) as e:
            raise CMHandlerConfigurationError(f"Can't open socket! {e}")

    def close(self) -> None:
        """
        Closes the communication between the PC and Arduino board.
        """
        self._connection.close()
        self.logger.debug("Connection closed.")

    def __del__(self):
        """
        Closes the serial communication between the PC and Arduino board.
        """
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the serial communication between the PC and Arduino Board, due to an exception occurrence.

        Args:
            exc_type (str): The exception type.

            exc_value: The value of the exception.

            traceback (str): The position in the code where the exception occurred.

        """
        self.close()

    def stop(self) -> None:
        """
        Releases the lock when signalled via an interrupt.
        """
        self.interrupted.set()

    def run(self) -> None:
        """
        Starts the Handler processing commands.
        """
        while not self.interrupted.is_set():
            self.process_data()
        self.close()

    def send(self, command_id: str, *arg) -> None:
        """
        Sends a command over the TCP/IP connection.

        Args:
            command_id: The ID of the command.

            *arg: Variable argument.

        """
        try:
            self.write(self.forge_command(command_id, *arg))
        except OSError as e:
            raise CMCommunicationError(f"Error writing to socket! {e}") from None

    def write(self, msg: str) -> None:
        """
        Writes raw data into the socket.

        Args:
            msg: The message to send.

        """
        self.logger.debug('Sending "%s" to "%s"', msg, self._connection.getpeername())
        self._connection.send(msg.encode())

    def process_data(self) -> None:
        """
        Gets the data from socket to be processed.
        """
        try:
            self.process_char(self._connection.recv(1))
        except socket.timeout:
            pass
        except OSError as e:
            raise CMCommunicationError(f"Error reading from socket! {e}")

    def wait_until_running(self) -> None:
        """
        Waits until the current thread is running.
        """
        self.interrupted.wait()


# Typing variable for either Serial or TCPIP CommandHandler
GenericCommandHandler = Union[SerialCommandHandler, TCPIPCommandHandler]
