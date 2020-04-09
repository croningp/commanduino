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

    ##
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
            # Get active channels mask as an int
            # And convert to eight-bit padded binary string("0b00000000")
            channels_mask = format(int(arg[0]), "#010b")
            # Chop off "0b" prefix
            channels_mask = channels_mask[2:]
            # Split to list of ints
            self.channels = [int(c) for c in channels_mask]
            self.channels_lock.ensure_released()

    def set_channels(self, *channels):
        """Sets the state of all I2C channels on the MUX.
        If an arguments is not supplied for the channel, it would be switched off.

        Args:
            *channels: List of integer channel states (e.g [1,0,0,1]) where index represents
            channel number, 0/1 - channel state.
        """
        # Map every channel state to 0 or 1
        command_args = []
        for value in channels:
            if value == 0 or value == 1:
                command_args.append(value)
            else:
                command_args.append(0)
        # Chop to 8 channels
        # This is actually checked on the Arduino side, so just not to send
        # unnecessary long strings
        command_args = command_args[:MAX_CHANNELS]
        self.send(CMD_SET_STATE, *command_args)
