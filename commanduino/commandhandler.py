"""

.. module:: commandhandler
   :platform: Unix
   :synopsis: Handles the communication to/from the Arduino Hardware.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
import time
import serial
import threading

from ._logger import create_logger

#Default delimiter to separate commands
DEFAULT_DELIM = ','

#Default terminal character of a command
DEFAULT_TERM = ';'

##Default decimal
DEFAULT_CMD_DECIMAL = 2

#Default baudrate for communication
DEFAULT_BAUDRATE = 115200

#Default timeout time
DEFAULT_TIMEOUT = 0.01


class CommandHandler(object):
    """
    Represents the Command Handler which will handle commands to/from the Arduino hardware.

    Args:
        delim (chr): Delimiter of the command, default set to DEFAULT_DELIM(',')

        term (chr): Terminal character of the command, set to DEFAULT_TERM(';')

        cmd_decimal (int): Decimal of the command, default set to DEFAULT_CMD_DECIMAL(2)

    """
    def __init__(self, delim=DEFAULT_DELIM, term=DEFAULT_TERM, cmd_decimal=DEFAULT_CMD_DECIMAL):
        self.logger = create_logger(self.__class__.__name__)

        self.delim = delim  # character separating args in a message
        self.term = term  # character ending a message

        self.buffer = ''  # string that will hold the received data

        self.handlers = {}
        self.relays = {}
        self.default_handlers = []

        self.cmd_header = ''
        self.cmd_decimal = cmd_decimal

    def process_char(self, a_char):
        """
        Processes a single character of a command.

        Args:
            a_char (chr): The character to be processed

        """
        if a_char:
            a_char = a_char.decode('utf-8')
            self.logger.debug('Processing "{}"'.format(a_char),
                              extra={'buffer': self.buffer})
            if a_char == self.term:
                self.handle(self.buffer)
                self.buffer = ''
            else:
                self.buffer += a_char

    def process_string(self, a_string):
        """
        Processes a full string in the command.

        Args:
            a_string (str): The string to be processed.

        """
        for a_char in a_string:
            self.process_char(a_char)

    def process_serial(self, a_serial):
        """
        Processes the serial communication to obtain data to be processed.

        Args:
            a_serial (int): The serial to read from.

        """
        self.process_char(a_serial.read(1))

    def handle(self, cmd):
        """
        Handles a full command to/from the Arduino hardware.

        Args:
            cmd (str): The command to be handled.

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

    def build_remaining(self, cmd_list):
        """
        Builds an Arduino command from a list of partial commands.

        Args:
            cmd_list (List): The list of command constituents.

        """
        return self.delim.join(cmd_list[1:]) + self.term

    def add_command(self, command_id, callback_function):
        """
        Adds an Arduino command to the Handler.

        Args:
            command_id (str): The ID of the command.

            callback_function (str): A copy of the command to "callback".

        """
        if command_id not in self.handlers:
            self.handlers[command_id] = []
        if callback_function not in self.handlers[command_id]:
            self.handlers[command_id].append(callback_function)

    def remove_command(self, command_id, callback_function):
        """
        Removes an Arduino command from the Handler.

        Args:
            command_id (str): The ID of the command.

            callback_function (str): A copy of the command to "callback".

        """
        if command_id in self.handlers:
            if callback_function in self.handlers[command_id]:
                self.handlers[command_id].remove(callback_function)

    def add_relay(self, command_id, callback_function):
        """
        Adds a relay to the Handler.

        Args:
            command_id (str): The ID of the command.

            callback_function (str): A copy of the command to "callback".

        """
        if command_id not in self.relays:
            self.relays[command_id] = []
        if callback_function not in self.relays[command_id]:
            self.relays[command_id].append(callback_function)

    def remove_relay(self, command_id, callback_function):
        """
        Removes a relay form the Handler.

        Args:
            command_id (str): The ID of the command.

            callback_function (str): A copy of the command to "callback".

        """
        if command_id in self.relays:
            if callback_function in self.relays[command_id]:
                self.relays[command_id].remove(callback_function)

    def add_default_handler(self, callback_function):
        """
        Adds a default handler to the device.

        Args:
            callback_function (str): A copy of the command to "callback".

        """
        if callback_function not in self.default_handlers:
            self.default_handlers.append(callback_function)

    def remove_default_handler(self, callback_function):
        """
        Removes a default handler from the device.

        Args:
            callback_function (str): A copy of the command to "callback".

        """
        if callback_function in self.default_handlers:
            self.default_handlers.remove(callback_function)

    #
    def set_command_header(self, cmd_header, addDelim=True):
        """
        Sets the header of the Arduino command.

        Args:
            cmd_header (chr): The header of the command.

            addDelim (bool): Adds a delimiter to the command, default set to True.

        """
        self.cmd_header = cmd_header
        if addDelim:
            self.cmd_header += self.delim
        self.logger.debug('Set command header to "{}"'.format(self.cmd_header))

    def set_command_decimal(self, cmd_decimal):
        """
        Sets the decimal of the Arduino command.

        Args:
            cmd_decimal (int): The decimal of the command.

        """
        self.cmd_decimal = cmd_decimal
        self.logger.debug('Set decimal to "{}"'.format(self.cmd_decimal))

    def forge_command(self, command_id, *args):
        """
        Creates a full Arduino command.

        Args:
            command_id (str): The ID of the command.

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
        port (str): The port to communicate over.

        baudrate (int): The baudrate of the serial communication, default set to DEFAULT_BAUDRATE (115200)

        timeout (float): The time to wait for timeout, default set to DEFAULT_TIMEOUT (0.01)

        delim (chr): The delimiting character of a command, default set to DEFAULT_DELIM (',')

        term (chr): The terminal character of a command, default set to DEFAULT_TERM (';')

        cmd_decimal (int): The decimal of the command, default set to DEFAULT_CMD_DECIMAL (2)

    """
    def __init__(self, port, baudrate=DEFAULT_BAUDRATE, timeout=DEFAULT_TIMEOUT, delim=DEFAULT_DELIM, term=DEFAULT_TERM, cmd_decimal=DEFAULT_CMD_DECIMAL):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.logger = create_logger(self.__class__.__name__)

        CommandHandler.__init__(self, delim, term, cmd_decimal)

        self.open(port, baudrate, timeout)

    @classmethod
    def from_config(cls, serialcommand_config):
        """
        Obtains the details of the handler from a configuration.

        Args:
            cls (Class): THe instantiating class.

            serialcommand_config (Dict): Dictionary containing the configuration details.

        Returns:
            SerialCommandHandler: New SerialCommandHandler object with details set from a configuration setup.

        """
        port = serialcommand_config['port']

        optionals = ['baudrate', 'timeout', 'delim', 'term']

        kwargs = {}
        for key in optionals:
            if key in serialcommand_config:
                kwargs[key] = serialcommand_config[key]

        return cls(port, **kwargs)

    def open(self, port, baudrate, timeout):
        """
        Opens the serial communication between the PC and Arduino board.

        Args:
            port (str): The port to communicate over.

            baudrate (int): The baudrate of serial communication.

            timeout (float): The time to wait for timeout.

        """
        self.logger.debug('Opening port {}'.format(port),
                          extra={'port': port,
                                 'baudrate': baudrate,
                                 'timeout': timeout})
        self._serial = serial.Serial(port, baudrate, timeout=timeout)

    def close(self):
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
        Closes the serial communication between the PC and Arduino Board, due to an exception occurence.

        Args:
            exc_type (str): The exception type.

            exc_value: The value of the exception.

            traceback (str): The position in the code where the exception occured.

        """
        self.close()

    def stop(self):
        """
        Releases the lock when signalled via an interrupt.
        """
        self.interrupted.release()

    def run(self):
        """
        Starts the Handler processing commands.
        """
        self.interrupted.acquire()
        while self.interrupted.locked():
            self.process_serial(self._serial)
        self.close()

    def send(self, command_id, *arg):
        """
        Sends a command over the serial communication.

        Args:
            command_id (str): The ID of the command.

            *arg: Variable argument.

        """
        self.write(self.forge_command(command_id, *arg))

    def write(self, msg):
        """
        Writes a message over the serial communication.

        Args:
            msg (str): The message to send.

        """
        self.logger.debug('Sending "{}" on port "{}"'.format(msg, self._serial.port))
        self._serial.write(msg.encode())

    def wait_until_running(self, sleep_time=0.01):
        """
        Waits until the current thread is running.

        Args:
            sleep_time (float): The time to wait for, default set to 0.01

        """
        while not self.interrupted.locked():
            time.sleep(sleep_time)
