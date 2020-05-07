"""

.. module:: CommandAccelStepper
   :platform: Unix
   :synopsis: Represents an Accelerator Stepper Arduino device.

.. moduleauthor:: Graham Keenan <1105045k@student.gla.ac.uk>

"""

from .commanddevice import CommandDevice

import time
import logging
module_logger = logging.getLogger(__name__)

# Bonjour information
BONJOUR_ID = 'ACCELSTEPPER'
CLASS_NAME = 'CommandAccelStepper'

# Incoming Commands
COMMANDACCELSTEPPER_SET_POSITION = "SP"
COMMANDACCELSTEPPER_SET_SPEED = "SS"
COMMANDACCELSTEPPER_SET_MAXSPEED = "SMS"
COMMANDACCELSTEPPER_SET_ACC = "SA"

COMMANDACCELSTEPPER_ENABLE_ACC = "EA"
COMMANDACCELSTEPPER_DISABLE_ACC = "DA"

COMMANDACCELSTEPPER_MOVE_TO = "MT"
COMMANDACCELSTEPPER_MOVE = "M"
COMMANDACCELSTEPPER_STOP = "S"

COMMANDACCELSTEPPER_REQUEST_MOVING = "RM"
COMMANDACCELSTEPPER_REQUEST_DIST = "RD"
COMMANDACCELSTEPPER_REQUEST_TARGET = "RT"
COMMANDACCELSTEPPER_REQUEST_POSITION = "RP"

COMMANDACCELSTEPPER_REQUEST_SPEED = "RIS"
COMMANDACCELSTEPPER_REQUEST_MAXSPEED = "RIMS"
COMMANDACCELSTEPPER_REQUEST_ACCELERATION = "RIA"


# Outgoing Commands
COMMANDACCELSTEPPER_MOVING = "M"
COMMANDACCELSTEPPER_DIST = "D"
COMMANDACCELSTEPPER_TARGET = "T"
COMMANDACCELSTEPPER_POSITION = "P"

COMMANDACCELSTEPPER_SPEED = "IS"
COMMANDACCELSTEPPER_MAXSPEED = "IMS"
COMMANDACCELSTEPPER_ACCELERATION = "IA"

# Default speed
DEFAULT_SPEED = 5000

# Default maximum speed
DEFAULT_MAX_SPEED = 5000

# Default acceleration
DEFAULT_ACCELERATION = 2000

# Default sleep time
DEFAULT_SLEEP_TIME = 0.1


class CommandAccelStepper(CommandDevice):
    """
    Accelerator Stepper Arduino Device

    Args:
        speed (int): Speed of the device, default set to DEFAULT_SPEED (5000).

        max_speed (int): Maximum speed of the device, default set to DEFAULT_MAX_SPEED (5000).

        acceleration (int): Speed of acceleration, default set to DEFAULT_ACCELERATION (2000).

        enabled_acceleration (bool): Acceleration enabled, default set to True.

        reverted_direction (bool): Direction is reversed, default set to False.

    Base:
        CommandDevice

    """
    def __init__(self, speed=DEFAULT_SPEED, max_speed=DEFAULT_MAX_SPEED, acceleration=DEFAULT_ACCELERATION, enabled_acceleration=True, reverted_direction=False):
        CommandDevice.__init__(self)
        self.register_all_requests()
        self.init_speed = speed
        self.init_max_speed = max_speed
        self.init_acceleration = acceleration
        self.enabled_acceleration = enabled_acceleration
        self.reverted_direction = reverted_direction

    def init(self):
        self.set_all_params()

    def set_all_params(self):
        """
        Sets all the parameters of the device automatically.
        """
        self.set_running_speed(self.init_speed)
        self.set_max_speed(self.init_max_speed)
        self.set_acceleration(self.init_acceleration)

        if self.enabled_acceleration:
            self.enable_acceleration()

    def apply_reverted_direction(self, value):
        """
        Reverses the direction of movement.

        Args:
            value (int): The current value.

        Returns:
            value (int): The new value (-value)

        """
        if self.reverted_direction:
            value = -value
        return value

    @property
    def is_moving(self):
        """
        Check for movement.

        Returns:
            bool: The movement state of the stepper.

        """
        return self.get_moving_state()

    def wait_until_idle(self):
        """
        Waits until the device is idle (not moving).
        """
        while self.is_moving:
            time.sleep(DEFAULT_SLEEP_TIME)

    def set_current_position(self, steps):
        """
        Sets the current position of the device.

        Args:
            steps (int): The current position, in steps

        """
        self.send(COMMANDACCELSTEPPER_SET_POSITION, steps)

    def _set_speed(self, steps_per_sec):
        """
        Sets the speed of the device.

        Args:
            steps_per_sec (int): The number of steps per second.

        """
        self.send(COMMANDACCELSTEPPER_SET_SPEED, steps_per_sec)

    def set_running_speed(self, steps_per_sec):
        """
        Sets the running speed of the device.

        Args:
            steps_per_sec (int): The number of steps per second.

        """
        self.running_speed = steps_per_sec

    def set_max_speed(self, steps_per_sec):
        """
        Sets the maximum speed of the device.

        Args:
            steps_per_sec (int): The number of steps per second.

        """
        self.send(COMMANDACCELSTEPPER_SET_MAXSPEED, steps_per_sec)

    def set_acceleration(self, steps_per_sec_per_sec):
        """
        Sets the acceleration speed of the device.

        Args:
            steps_per_sec_per_sec (int): The number of steps per second, per second.

        """
        self.send(COMMANDACCELSTEPPER_SET_ACC, steps_per_sec_per_sec)

    def enable_acceleration(self):
        """
        Enables acceleration on the device.
        """
        self.wait_until_idle()
        self.send(COMMANDACCELSTEPPER_ENABLE_ACC)
        # Bug in the stepper motor
        self.stop()
        self.enabled_acceleration = True

    def disable_acceleration(self):
        """
        Disables acceleration on the device.
        """
        self.wait_until_idle()
        self.send(COMMANDACCELSTEPPER_DISABLE_ACC)
        # Bug in the stepper motor
        self.stop()
        self.enabled_acceleration = False

    def move_to(self, steps, wait=True):
        """
        Moves the device to a specific point.

        Args:
            steps (int): The position to move to.

            wait (bool): Wait until the device is idle, default set to True.

        """
        running_speed = self.apply_reverted_direction(self.running_speed)
        self._set_speed(running_speed)
        steps = self.apply_reverted_direction(steps)
        self.send(COMMANDACCELSTEPPER_MOVE_TO, steps)
        if wait:
            self.wait_until_idle()

    def move(self, steps, wait=True):
        """
        Moves the device a certain number of steps.

        Args:
            steps (int): The number of steps to move.

            wait (bool): Wait for the device to be idle, default set to True.

        """
        running_speed = self.apply_reverted_direction(self.running_speed)
        self._set_speed(running_speed)
        steps = self.apply_reverted_direction(steps)
        self.send(COMMANDACCELSTEPPER_MOVE, steps)
        if wait:
            self.wait_until_idle()

    def stop(self, wait=True):
        """
        Stops the device.

        Args:
            wait (bool): Wait until the device is idle, default set to True.

        """
        self.send(COMMANDACCELSTEPPER_STOP)
        if wait:
            self.wait_until_idle()

    def register_all_requests(self):
        """
        Registers all requests to the device.
        """
        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_MOVING,
            COMMANDACCELSTEPPER_MOVING,
            'moving_state',
            self.handle_moving_state_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_DIST,
            COMMANDACCELSTEPPER_DIST,
            'distance_to_go',
            self.handle_distance_to_go_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_TARGET,
            COMMANDACCELSTEPPER_TARGET,
            'target_position',
            self.handle_target_position_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_POSITION,
            COMMANDACCELSTEPPER_POSITION,
            'current_position',
            self.handle_current_position_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_SPEED,
            COMMANDACCELSTEPPER_SPEED,
            'speed',
            self.handle_speed_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_MAXSPEED,
            COMMANDACCELSTEPPER_MAXSPEED,
            'max_speed',
            self.handle_max_speed_command)

        self.register_request(
            COMMANDACCELSTEPPER_REQUEST_ACCELERATION,
            COMMANDACCELSTEPPER_ACCELERATION,
            'acceleration',
            self.handle_acceleration_command)

    def handle_moving_state_command(self, *arg):
        """
        Handles the command for the moving state.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.moving_state = bool(int(arg[0]))
            self.moving_state_lock.ensure_released()

    def handle_distance_to_go_command(self, *arg):
        """
        Handles the command for distance to go.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.distance_to_go = self.apply_reverted_direction(int(arg[0]))
            self.distance_to_go_lock.ensure_released()

    def handle_target_position_command(self, *arg):
        """
        Handles the command for the target position.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.target_position = self.apply_reverted_direction(int(arg[0]))
            self.target_position_lock.ensure_released()

    def handle_current_position_command(self, *arg):
        """
        Handles the command for the current position.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.current_position = self.apply_reverted_direction(int(arg[0]))
            self.current_position_lock.ensure_released()

    def handle_speed_command(self, *arg):
        """
        Handles the command for the speed.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.speed = self.apply_reverted_direction(float(arg[0]))
            self.speed_lock.ensure_released()

    def handle_max_speed_command(self, *arg):
        """
        Handles the command for the maximum speed.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.max_speed = float(arg[0])
            self.max_speed_lock.ensure_released()

    def handle_acceleration_command(self, *arg):
        """
        Handles the command for the acceleration.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.acceleration = float(arg[0])
            self.acceleration_lock.ensure_released()

    def print_info(self):
        """
        Prints the current information for the device.
        """
        print('###')
        print('moving_state: ', self.get_moving_state())
        print('distance_to_go: ',  self.get_distance_to_go())
        print('target_position: ', self.get_target_position())
        print('current_position: ', self.get_current_position())
        print('speed: ',  self.get_speed())
        print('max_speed: ', self.get_max_speed())
        print('acceleration: ',  self.get_acceleration())
        print('###')
