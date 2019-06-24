"""

.. module:: CommandDigitalRead
   :platform: Unix
   :synopsis: Represents a DigitalRead Arduino Device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# Bonjour Information
BONJOUR_ID = 'DIGITALREAD'
CLASS_NAME = 'CommandDigitalRead'

# Incoming
CMD_ANSWER_STATE = 'S'

# Outgoing
CMD_REQUEST_STATE = 'R'


class CommandDigitalRead(CommandDevice):
    """
    DigitalRead Arduino device.

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
            'state',
            self.handle_state_command)

    def handle_state_command(self, *arg):
        """
        Handles the state setting command.

        Args:
            *arg: Variable command.
        """
        if arg[0]:
            self.state = bool(int(arg[0]))
            self.state_lock.ensure_released()
