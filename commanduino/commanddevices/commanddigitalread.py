from commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)


# bonjour info
BONJOUR_ID = 'DIGITALREAD'
CLASS_NAME = 'CommandDigitalRead'

# incoming
CMD_ANSWER_STATE = 'S'

# outgoing
CMD_REQUEST_STATE = 'R'


class CommandDigitalRead(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    ##
    def register_all_requests(self):
        self.register_request(
            CMD_REQUEST_STATE,
            CMD_ANSWER_STATE,
            'state',
            self.handle_state_command)

    def handle_state_command(self, *arg):
        if arg[0]:
            self.state = bool(int(arg[0]))
            self.state_lock.ensure_released()
