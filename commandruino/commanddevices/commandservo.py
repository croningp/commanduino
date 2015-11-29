from commanddevice import CommandDevice
from ..lock import Lock

import logging
module_logger = logging.getLogger(__name__)

# incoming
CMD_ANSWER_ANGLE = 'A'

# outgoing
CMD_SET_ANGLE = 'W'
CMD_REQUEST_ANGLE = 'R'

DEFAULT_SLEEP_TIME = 0.01
DEFAULT_TIMEOUT = 1


class CommandServo(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)

        # angle
        self.angle = 0
        self.angle_lock = Lock()
        self.cmdHdl.add_command(CMD_ANSWER_ANGLE, self.handle_angle_command)

    ##
    def request_angle(self):
        self.send(CMD_REQUEST_ANGLE)

    def handle_angle_command(self, *arg):
        if arg[0]:
            self.angle = int(arg[0])
            self.angle_lock.ensure_released()

    def set_angle(self, angle):
        self.send(CMD_SET_ANGLE, int(angle))

    def get_angle(self):
        self.angle_lock.acquire()
        self.request_angle()
        is_valid, elapsed = self.angle_lock.wait_until_released()
        self.angle_lock.ensure_released()
        return self.angle, is_valid, elapsed
