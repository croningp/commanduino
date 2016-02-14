from commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# outgoing
CMD_SET_LEVEL = 'W'


class CommandDigitalWrite(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)

    ##
    def set_level(self, level):
        self.send(CMD_SET_LEVEL, int(bool(level)))

    def low(self):
        self.set_level(0)

    def high(self):
        self.set_level(1)
