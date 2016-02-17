from commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# outgoing
CMD_SET_LEVEL = 'W'


class CommandAnalogWrite(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)

    ##
    def set_pwm_value(self, value):
        casted_value = max(min(value, 255), 0)
        self.send(CMD_SET_LEVEL, casted_value)
