from ..commandhandler import CommandHandler

import logging
module_logger = logging.getLogger(__name__)


class CommandDevice(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.cmdHdl = CommandHandler()
        self.cmdHdl.add_default_handler(self.unrecognized)

    @classmethod
    def from_config(cls, config):
        return cls()

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
