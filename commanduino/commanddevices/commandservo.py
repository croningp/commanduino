"""
.. module:: CommandServo
   :platform: Unix
   :synopsis: Represents a Servo Arduino device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# Bonjour Information
BONJOUR_ID = 'SERVO'
CLASS_NAME = 'CommandServo'

# Incoming
CMD_ANSWER_ANGLE = 'A'

# Outgoing
CMD_SET_ANGLE = 'W'
CMD_REQUEST_ANGLE = 'R'


class CommandServo(CommandDevice):
    """
    Servo Arduino device.
    """
    def __init__(self, initial_angle=90, min_limit=0, max_limit=180):
        CommandDevice.__init__(self)
        self.register_all_requests()
        self.min_limit = 0
        self.max_limit = 0
        self.limit = False

        # From config
        self.set_limit(minimum=min_limit, maximum=max_limit)  # If limits other than 0-180 are set than self.limit=True
        self.initial_angle = initial_angle
        
        self.clamp = lambda n, minimum, maximum: max(min(maximum, n), minimum)

    def init(self):
        self.set_angle(self.initial_angle)

    # Sets the limits of the device
    def set_limit(self, minimum, maximum):
        if minimum > 0 and maximum < 180:
            self.min_limit = minimum
            self.max_limit = maximum
            self.limit = True
            return True
        else:
            return False

    # Removes limits
    def remove_limit(self):
        self.limit = False

    ##
    def set_angle(self, angle):
        """
        Sets the angle of the device.

        Args:
            angle (float): Angle to set the device to.

        """
        if self.limit is True:
            angle = self.clamp(angle, self.min_limit, self.max_limit)
            self.send(CMD_SET_ANGLE, int(angle))
        else:
            self.send(CMD_SET_ANGLE, int(angle))

    def register_all_requests(self):
        """
        Registers all requests to the device for later use.
        """
        self.register_request(
            CMD_REQUEST_ANGLE,
            CMD_ANSWER_ANGLE,
            'angle',
            self.handle_angle_command)

    def handle_angle_command(self, *arg):
        """
        Handles the command for the angle.

        Args:
            *arg: Variable argument.

        """
        if arg[0]:
            self.angle = int(arg[0])
            self.angle_lock.ensure_released()
