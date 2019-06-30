"""

.. module:: CommandAnalogWrite
   :platform: Unix
   :synopsis: Represents an AnalogWrite Arduino Device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# Bonjour Information
BONJOUR_ID = 'ANALOGWRITE'
CLASS_NAME = 'CommandAnalogWrite'

# Outgoing (Write)
CMD_SET_LEVEL = 'W'


class CommandAnalogWrite(CommandDevice):
    """
    AnalogWrite Arduino device.

    Base:
        CommandDevice
    """
    def __init__(self):
        CommandDevice.__init__(self)

    ##
    def set_pwm_value(self, value):
        """
        Sets the pwm value.

        Args:
            value: The value to set.

        """
        casted_value = max(min(value, 255), 0)
        self.send(CMD_SET_LEVEL, casted_value)
