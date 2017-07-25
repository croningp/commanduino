from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# bonjour info
BONJOUR_ID = 'DALLAS'
CLASS_NAME = 'CommandDallas'

# incoming
CMD_ANSWER_CELSIUS = 'C'

# outgoing
CMD_REQUEST_CELSIUS = 'RC'


class CommandDallas(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    def register_all_requests(self):
        self.register_request(
            CMD_REQUEST_CELSIUS,
            CMD_ANSWER_CELSIUS,
            'celsius',
            self.handle_celsius_command)

    def handle_celsius_command(self, *arg):
        if arg[0]:
            self.celsius = float(arg[0])
            self.celsius_lock.ensure_released()
