from commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# bonjour info
BONJOUR_ID = 'ANALOGREAD'
CLASS_NAME = 'CommandAnalogRead'

# incoming
CMD_ANSWER_LEVEL = 'L'

# outgoing
CMD_REQUEST_LEVEL = 'R'


class CommandAnalogRead(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    ##
    def register_all_requests(self):
        self.register_request(
            CMD_REQUEST_LEVEL,
            CMD_ANSWER_LEVEL,
            'level',
            self.handle_level_command)

    def handle_level_command(self, *arg):
        if arg[0]:
            self.level = int(arg[0])
            self.level_lock.ensure_released()
