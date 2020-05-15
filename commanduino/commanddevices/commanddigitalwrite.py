"""

.. module:: CommandDigitalWrite
   :platform: Unix
   :synopsis: Represents a DigitalWrite Arduino device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# Bonjour Information
BONJOUR_ID = 'DIGITALWRITE'
CLASS_NAME = 'CommandDigitalWrite'

# Outgoing (Write)
CMD_SET_LEVEL = 'W'


class CommandDigitalWrite(CommandDevice):
    """
    DigitalWrite Arduino device.

    Base:
        CommandDevice
    """
    def __init__(self):
        CommandDevice.__init__(self)

    def set_level(self, level: int) -> None:
        """
        Sets the level of the device.

        Args:
            level (int): The level setting.

        """
        self.send(CMD_SET_LEVEL, int(bool(level)))

    def low(self):
        """
        Sets the level to LOW.
        """
        self.set_level(0)

    def high(self):
        """
        Sets the level to HIGH.
        """
        self.set_level(1)
