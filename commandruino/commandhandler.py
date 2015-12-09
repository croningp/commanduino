import time
import serial
import threading

import logging
module_logger = logging.getLogger(__name__)

DEFAULT_DELIM = ','
DEFAULT_TERM = ';'
DEFAULT_CMD_DECIMAL = 2

DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 0.01


class CommandHandler(object):

    def __init__(self, delim=DEFAULT_DELIM, term=DEFAULT_TERM):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.delim = delim  # character separating args in a message
        self.term = term  # character ending a message

        self.buffer = ''  # string that will hold the received data

        self.handlers = {}
        self.relays = {}
        self.default_handlers = []

        self.cmd_header = ''
        self.cmd_decimal = DEFAULT_CMD_DECIMAL

    def process_char(self, a_char):
        if a_char:
            self.logger.debug('Processing "{}"'.format(a_char),
                              extra={'buffer': self.buffer})
            if a_char == self.term:
                self.handle(self.buffer)
                self.buffer = ''
            else:
                self.buffer += a_char

    def process_string(self, a_string):
        for a_char in a_string:
            self.process_char(a_char)

    def process_serial(self, a_serial):
        self.process_char(a_serial.read(1))

    def handle(self, cmd):
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
        return self.delim.join(cmd_list[1:]) + self.term

    def add_command(self, command_id, callback_function):
        if command_id not in self.handlers:
            self.handlers[command_id] = []
        if callback_function not in self.handlers[command_id]:
            self.handlers[command_id].append(callback_function)

    def remove_command(self, command_id, callback_function):
        if command_id in self.handlers:
            if callback_function in self.handlers[command_id]:
                self.handlers[command_id].remove(callback_function)

    def add_relay(self, command_id, callback_function):
        if command_id not in self.relays:
            self.relays[command_id] = []
        if callback_function not in self.relays[command_id]:
            self.relays[command_id].append(callback_function)

    def remove_relay(self, command_id, callback_function):
        if command_id in self.relays:
            if callback_function in self.relays[command_id]:
                self.relays[command_id].remove(callback_function)

    def add_default_handler(self, callback_function):
        if callback_function not in self.default_handlers:
            self.default_handlers.append(callback_function)

    def remove_default_handler(self, callback_function):
        if callback_function in self.default_handlers:
            self.default_handlers.remove(callback_function)

    #
    def set_command_header(self, cmd_header, addDelim=True):
        self.cmd_header = cmd_header
        if addDelim:
            self.cmd_header += self.delim
        self.logger.debug('Set command header to "{}"'.format(self.cmd_header))

    def set_command_decimal(self, cmd_decimal):
        self.cmd_decimal = cmd_decimal
        self.logger.debug('Set decimal to "{}"'.format(self.cmd_decimal))

    def forge_command(self, command_id, *args):
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

    def __init__(self, port, baudrate=DEFAULT_BAUDRATE, timeout=DEFAULT_TIMEOUT, delim=DEFAULT_DELIM, term=DEFAULT_TERM):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.logger = logging.getLogger(self.__class__.__name__)

        CommandHandler.__init__(self, delim, term)

        self.open(port, baudrate, timeout)

    @classmethod
    def from_config(cls, serialcommand_config):
        port = serialcommand_config['port']

        optionals = ['baudrate', 'timeout', 'delim', 'term']

        kwargs = {}
        for key in optionals:
            if key in serialcommand_config:
                kwargs[key] = serialcommand_config[key]

        return cls(port, **kwargs)

    def open(self, port, baudrate, timeout):
        self.logger.debug('Opening port {}'.format(port),
                          extra={'port': port,
                                 'baudrate': baudrate,
                                 'timeout': timeout})
        self._serial = serial.Serial(port, baudrate, timeout=timeout)

    def close(self):
        if hasattr(self, "_serial"):
            self._serial.close()
            self.logger.debug('Closing port "{}"'.format(self._serial.port))

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def stop(self):
        self.interrupted.release()

    def run(self):
        self.interrupted.acquire()
        while self.interrupted.locked():
            self.process_serial(self._serial)
        self.close()

    def send(self, command_id, *arg):
        self.write(self.forge_command(command_id, *arg))

    def write(self, msg):
        self.logger.debug('Sending "{}" on port "{}"'.format(msg, self._serial.port))
        self._serial.write(msg.encode())

    def wait_until_running(self, sleep_time=0.01):
        while not self.interrupted.locked():
            time.sleep(sleep_time)
