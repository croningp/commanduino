"""

.. module:: CommandLinearAccelStepper
   :platform: Unix
   :synopsis: Represents a Linear AccelStepper Arduino device.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

from .commanddevice import CommandDevice

import time

import logging
module_logger = logging.getLogger(__name__)

# bonjour info
BONJOUR_ID = 'LINEARACCELSTEPPER'
CLASS_NAME = 'CommandLinearAccelStepper'

# Incoming Commands
COMMANDLINEARACCELSTEPPER_SET_POSITION = "SP"
COMMANDLINEARACCELSTEPPER_SET_SPEED = "SS"
COMMANDLINEARACCELSTEPPER_SET_MAX_SPEED = "SMS"
COMMANDLINEARACCELSTEPPER_SET_ACC = "SA"

COMMANDLINEARACCELSTEPPER_ENABLE_ACC = "EA"
COMMANDLINEARACCELSTEPPER_DISABLE_ACC = "DA"
COMMANDLINEARACCELSTEPPER_ENABLE_SWITCH = "ES"
COMMANDLINEARACCELSTEPPER_DISABLE_SWITCH = "DS"

COMMANDLINEARACCELSTEPPER_HOME = "H"
COMMANDLINEARACCELSTEPPER_MOVE_TO = "MT"
COMMANDLINEARACCELSTEPPER_MOVE = "M"
COMMANDLINEARACCELSTEPPER_STOP = "S"

COMMANDLINEARACCELSTEPPER_REQUEST_SWITCH = "RS"
COMMANDLINEARACCELSTEPPER_REQUEST_MOVING = "RM"
COMMANDLINEARACCELSTEPPER_REQUEST_DIST = "RD"
COMMANDLINEARACCELSTEPPER_REQUEST_TARGET = "RT"
COMMANDLINEARACCELSTEPPER_REQUEST_POSITION = "RP"

COMMANDLINEARACCELSTEPPER_REQUEST_SPEED = "RIS"
COMMANDLINEARACCELSTEPPER_REQUEST_MAXSPEED = "RIMS"
COMMANDLINEARACCELSTEPPER_REQUEST_ACCELERATION = "RIA"

# Outgoing Commands
COMMANDLINEARACCELSTEPPER_SWITCH = "S"
COMMANDLINEARACCELSTEPPER_MOVING = "M"
COMMANDLINEARACCELSTEPPER_DIST = "D"
COMMANDLINEARACCELSTEPPER_TARGET = "T"
COMMANDLINEARACCELSTEPPER_POSITION = "P"

COMMANDLINEARACCELSTEPPER_SPEED = "IS"
COMMANDLINEARACCELSTEPPER_MAXSPEED = "IMS"
COMMANDLINEARACCELSTEPPER_ACCELERATION = "IA"

# Default speed
DEFAULT_SPEED = 5000

# Default maximum speed
DEFAULT_MAX_SPEED = 5000

# Default acceleration
DEFAULT_ACCELERATION = 2000

# Default homing speed
DEFAULT_HOMING_SPEED = 2000

# Default sleep time
DEFAULT_SLEEP_TIME = 0.1  # let's not make it too low to not make the communication bus too busy


class CommandLinearAccelStepper(CommandDevice):
    """
    Linear Accelerator Stepper Arduino device.

    Args:
        speed (int): Speed of the device, default set to DEFAULT_SPEED (5000)

        max_speed (int): Maximum speed of the device, default set to DEFAULT_MAX_SPEED (5000)

        acceleration (int): Speed of acceleration, default set to DEFAULT_ACCELERATION (2000)

        homing_speed (int): Homing speed of the device, default set to DEFAULT_HOMING_SPEED (2000)

        enabled_acceleration (bool): Acceleration enabled, default set to True.

        reverted_direction (bool): Direction is reverted, default set to False.

        reverted_switch (bool): Switch is reverted, default set to False.

    Base:
        CommandDevice
    """
    def __init__(self, speed=DEFAULT_SPEED, max_speed=DEFAULT_MAX_SPEED, acceleration=DEFAULT_ACCELERATION, homing_speed=DEFAULT_HOMING_SPEED, enabled_acceleration=True, reverted_direction=False, reverted_switch=False):
        CommandDevice.__init__(self)
        self.register_all_requests()

        self.init_speed = speed
        self.init_max_speed = max_speed
        self.init_acceleration = acceleration
        self.homing_speed = homing_speed
        self.enabled_acceleration = enabled_acceleration
        self.reverted_direction = reverted_direction
        self.reverted_switch = reverted_switch

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
        else:
            self.disable_acceleration()

        if self.reverted_switch:
            self.enable_revert_switch()
        else:
            self.disable_revert_switch()

    def apply_reverted_direction(self, value):
        """
        Reverts the direction of movement.

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
        Check for movement in device.

        Returns:
            self.get_moving_state(): The movement state.
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
            steps (int): The position to move to.

        """
        self.send(COMMANDLINEARACCELSTEPPER_SET_POSITION, steps)

    def _set_speed(self, steps_per_second):
        """
        Sets the speed of the device.

        Args:
            steps_per_second (int): The number of steps per second to move.

        """
        self.send(COMMANDLINEARACCELSTEPPER_SET_SPEED, steps_per_second)

    def set_running_speed(self, steps_per_second):
        """
        Sets the running speed of the device.

        Args:
            steps_per_second (int): The number of steps per second.

        """
        self.running_speed = steps_per_second

    def set_homing_speed(self, steps_per_second):
        """
        Sets the homing speed of the device.

        Args:
            steps_per_second (int): The number of steps per second.

        """
        self.homing_speed = steps_per_second

    def set_max_speed(self, steps_per_second):
        """
        Sets the maximum speed of the device.

        Args:
            steps_per_second (int): The number of steps per second.

        """
        self.send(COMMANDLINEARACCELSTEPPER_SET_MAX_SPEED, steps_per_second)

    def set_acceleration(self, steps_per_second_per_second):
        """
        Sets the acceleration speed of the device.

        Args:
            steps_per_second_per_second (int): The number of steps per second per second.

        """
        self.send(COMMANDLINEARACCELSTEPPER_SET_ACC, steps_per_second_per_second)

    def enable_acceleration(self):
        """
        Enables acceleration on the device.
        """
        self.wait_until_idle()
        self.send(COMMANDLINEARACCELSTEPPER_ENABLE_ACC)
        # small bug here, better to run stop(), the stepper has a small velocity, seems to be a bug in accel stepper
        self.stop()
        self.enabled_acceleration = True

    def disable_acceleration(self):
        """
        Disables acceleration on the device.
        """
        self.wait_until_idle()
        self.send(COMMANDLINEARACCELSTEPPER_DISABLE_ACC)
        # small bug here, better to run stop(), the stepper has a small velocity, seems to be a bug in accel stepper
        self.stop()
        self.enabled_acceleration = False

    def enable_revert_switch(self):
        """
        Enables switch reversion on the device.
        """
        self.reverted_switch = True
        self.send(COMMANDLINEARACCELSTEPPER_ENABLE_SWITCH)

    def disable_revert_switch(self):
        """
        Disables switch reversion on the device.
        """
        self.reverted_switch = False
        self.send(COMMANDLINEARACCELSTEPPER_DISABLE_SWITCH)

    def home(self, wait=True):
        """
        Homes the device.

        Args:
            wait (bool): Wait for the device to be idle, default set to True.

        """
        homing_speed = self.apply_reverted_direction(self.homing_speed)
        self._set_speed(-homing_speed)
        self.send(COMMANDLINEARACCELSTEPPER_HOME)
        if wait:
            self.wait_until_idle()

    def move_to(self, steps, wait=True):
        """
        Moves the device to a specific point.

        Args:
            steps (int): The position to move to.

            wait (bool): Wait until the device is idle, default set to True.

        """
        # if not self.enabled_acceleration:
        running_speed = self.apply_reverted_direction(self.running_speed)
        self._set_speed(running_speed)
        steps = self.apply_reverted_direction(steps)
        self.send(COMMANDLINEARACCELSTEPPER_MOVE_TO, steps)
        if wait:
            self.wait_until_idle()

    def move(self, steps, wait=True):
        """
        Moves the device a certain number of steps.

        Args:
            steps (int): The number of steps to move.

            wait (bool): Waits for the device to be idle, default set to True.

        """
        # if not self.enabled_acceleration:
        running_speed = self.apply_reverted_direction(self.running_speed)
        self._set_speed(running_speed)
        steps = self.apply_reverted_direction(steps)
        self.send(COMMANDLINEARACCELSTEPPER_MOVE, steps)
        if wait:
            self.wait_until_idle()

    def stop(self, wait=True):
        """
        Stops the movement of the device.

        Args:
            wait (bool): Wait until the device is idle, default set to True.

        """
        self.send(COMMANDLINEARACCELSTEPPER_STOP)
        if wait:
            self.wait_until_idle()

    def register_all_requests(self):
        """
        Registers all requests to the device for later access.
        """
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_SWITCH,
            COMMANDLINEARACCELSTEPPER_SWITCH,
            'switch_state',
            self.handle_switch_state_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_MOVING,
            COMMANDLINEARACCELSTEPPER_MOVING,
            'moving_state',
            self.handle_moving_state_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_DIST,
            COMMANDLINEARACCELSTEPPER_DIST,
            'distance_to_go',
            self.handle_distance_to_go_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_TARGET,
            COMMANDLINEARACCELSTEPPER_TARGET,
            'target_position',
            self.handle_target_position_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_POSITION,
            COMMANDLINEARACCELSTEPPER_POSITION,
            'current_position',
            self.handle_current_position_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_SPEED,
            COMMANDLINEARACCELSTEPPER_SPEED,
            'speed',
            self.handle_speed_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_MAXSPEED,
            COMMANDLINEARACCELSTEPPER_MAXSPEED,
            'max_speed',
            self.handle_max_speed_command)
        self.register_request(
            COMMANDLINEARACCELSTEPPER_REQUEST_ACCELERATION,
            COMMANDLINEARACCELSTEPPER_ACCELERATION,
            'acceleration',
            self.handle_acceleration_command)

    def handle_switch_state_command(self, *arg):
        """
        Handles the command for switch state.

        Args:
            arg*: Variable command.

        """
        if arg[0]:
            self.switch_state = bool(int(arg[0]))
            self.switch_state_lock.ensure_released()

    def handle_moving_state_command(self, *arg):
        """
        Handles the command for moving state.

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
            *arg: variable command.

        """
        if arg[0]:
            self.distance_to_go = self.apply_reverted_direction(int(arg[0]))
            self.distance_to_go_lock.ensure_released()

    def handle_target_position_command(self, *arg):
        """
        Handles the command for target position.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.target_position = self.apply_reverted_direction(int(arg[0]))
            self.target_position_lock.ensure_released()

    def handle_current_position_command(self, *arg):
        """
        Handles the command for current position.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.current_position = self.apply_reverted_direction(int(arg[0]))
            self.current_position_lock.ensure_released()

    def handle_speed_command(self, *arg):
        """
        Handles the command for speed.

        Args:
            *arg: Variable command.

        """
        if arg[0]:
            self.speed = self.apply_reverted_direction(float(arg[0]))
            self.speed_lock.ensure_released()

    def handle_max_speed_command(self, *arg):
        """
        Handles the command for maximum speed.

        Args:
            *arg: Variable argument.

        """
        if arg[0]:
            self.max_speed = float(arg[0])
            self.max_speed_lock.ensure_released()

    def handle_acceleration_command(self, *arg):
        """
        Handles the command for acceleration.

        Args:
            *arg: Variable argument.
        """
        if arg[0]:
            self.acceleration = float(arg[0])
            self.acceleration_lock.ensure_released()

    def __str__(self):
        """
        Prints the current information for the device.
        """
        return "###\n" \
               "switch_state: " + str(self.get_switch_state()) + "\n" \
               "moving_state: " + str(self.get_moving_state()) + "\n" \
               "distance_to_go: " + str(self.get_distance_to_go()) + "\n" \
               "target_position: " + str(self.get_target_position()) + "\n" \
               "current_position: " + str(self.get_current_position()) + "\n" \
               "speed: " + str(self.get_speed()) + "\n" \
               "max_speed: " + str(self.get_max_speed()) + "\n" \
               "acceleration: " + str(self.get_acceleration()) + "\n" \
               "###"
