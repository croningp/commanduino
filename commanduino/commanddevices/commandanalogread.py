"""

.. module:: CommandAnalogRead
   :platform: Unix
   :synopsis: Represents an AnalogRead Arduino device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# Bonjour information
BONJOUR_ID = 'ANALOGREAD'
CLASS_NAME = 'CommandAnalogRead'

# Incoming (Level)
CMD_ANSWER_LEVEL = 'L'

# Outgoing (Read)
CMD_REQUEST_LEVEL = 'R'


class CommandAnalogRead(CommandDevice):
    """
    AnalogRead Arduino device.

    Base:
        CommandDevice

    """
    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    ##
    def register_all_requests(self):
        """
        Registers all requests to the device.
        """
        self.register_request(
            CMD_REQUEST_LEVEL,
            CMD_ANSWER_LEVEL,
            'level',
            self.handle_level_command)

    def handle_level_command(self, *arg):
        """
        Handles the level command.

        Args:
            *arg: Variable Argument.
        """
        if arg[0]:
            self.level = int(arg[0])
            self.level_lock.ensure_released()
