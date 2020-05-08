"""

.. module:: CommandPCA9548A
   :platform: Unix
   :synopsis: Represents a PCA9548A Arduino Device.

.. moduleauthor:: Sergey Zalesskiy <Sergey.Zalesskiy@glasgow.ac.uk>

"""

from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# Bonjour Information
BONJOUR_ID = 'PCA9548A'
CLASS_NAME = 'CommandPCA9548A'

# Incoming
CMD_ANSWER_STATE = 'C'

# Outgoing
CMD_REQUEST_STATE = 'R'
CMD_SET_STATE = 'W'

# Max channels on the mux
MAX_CHANNELS = 8


class CommandPCA9548A(CommandDevice):
    """
    PCA9548A Arduino device.

    Base:
        CommandDevice
    """
    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    def register_all_requests(self):
        """
        Registers all requests.
        """
        self.register_request(
            CMD_REQUEST_STATE,
            CMD_ANSWER_STATE,
            'channels',
            self.handle_get_channels)

    def handle_get_channels(self, *arg):
        """
        Handles the state setting command.

        Args:
            *arg: Variable command.
        """
        if arg[0]:
            # This would be a one byte representing active channels mask
            self.channels = int(arg[0])
            self.channels_lock.ensure_released()

    def set_channels(self, channels):
        """Sets the state of all I2C channels on the MUX.

        Args:
            channels: An integer representing an 8-bit long mask of channels to switch on/off.
            Anything bigger than 2^8=255 is set to zero on Arduino side anyway.
        """
        if channels > 255:
            channels = 0
        self.send(CMD_SET_STATE, channels)
