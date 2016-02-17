from commanddevice import CommandDevice
from ..lock import Lock

import logging
module_logger = logging.getLogger(__name__)

# incoming
CMD_ANSWER_ANGLE = 'A'

# outgoing
CMD_SET_ANGLE = 'W'
CMD_REQUEST_ANGLE = 'R'


class CommandServo(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    ##
    def set_angle(self, angle):
        self.send(CMD_SET_ANGLE, int(angle))

    def register_all_requests(self):
        self.register_request(
            CMD_REQUEST_ANGLE,
            CMD_ANSWER_ANGLE,
            'angle',
            self.handle_angle_command)

    def handle_angle_command(self, *arg):
        if arg[0]:
            self.angle = int(arg[0])
            self.angle_lock.ensure_released()
