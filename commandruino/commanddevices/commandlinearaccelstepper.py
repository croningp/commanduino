from commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# incoming command
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

# outgoing command
COMMANDLINEARACCELSTEPPER_SWITCH = "S"
COMMANDLINEARACCELSTEPPER_MOVING = "M"
COMMANDLINEARACCELSTEPPER_DIST = "D"
COMMANDLINEARACCELSTEPPER_TARGET = "T"
COMMANDLINEARACCELSTEPPER_POSITION = "P"


class CommandLinearAccelStepper(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    def set_current_position(self, steps):
        self.send(COMMANDLINEARACCELSTEPPER_SET_POSITION, steps)

    def set_speed(self, steps_per_second):
        self.send(COMMANDLINEARACCELSTEPPER_SET_SPEED, steps_per_second)

    def set_max_speed(self, steps_per_second):
        self.send(COMMANDLINEARACCELSTEPPER_SET_MAX_SPEED, steps_per_second)

    def set_acceleration(self, steps_per_second_per_second):
        self.send(COMMANDLINEARACCELSTEPPER_SET_ACC, steps_per_second_per_second)

    def enable_acceleration(self):
        self.send(COMMANDLINEARACCELSTEPPER_ENABLE_ACC)

    def disable_acceleration(self):
        self.send(COMMANDLINEARACCELSTEPPER_DISABLE_ACC)

    def enable_revert_switch(self):
        self.send(COMMANDLINEARACCELSTEPPER_ENABLE_SWITCH)

    def disable_revert_switch(self):
        self.send(COMMANDLINEARACCELSTEPPER_DISABLE_SWITCH)

    def home(self):
        self.send(COMMANDLINEARACCELSTEPPER_HOME)

    def move_to(self, steps):
        self.send(COMMANDLINEARACCELSTEPPER_MOVE_TO, steps)

    def move(self, steps):
        self.send(COMMANDLINEARACCELSTEPPER_MOVE, steps)

    def stop(self):
        self.send(COMMANDLINEARACCELSTEPPER_STOP)

    def register_all_requests(self):
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
            'distance_to_goal',
            self.handle_distance_to_goal_command)
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

    def handle_switch_state_command(self, *arg):
        if arg[0]:
            self.switch_state = bool(int(arg[0]))
            self.switch_state_lock.ensure_released()

    def handle_moving_state_command(self, *arg):
        if arg[0]:
            self.moving_state = bool(int(arg[0]))
            self.moving_state_lock.ensure_released()

    def handle_distance_to_goal_command(self, *arg):
        if arg[0]:
            self.distance_to_goal = int(arg[0])
            self.distance_to_goal_lock.ensure_released()

    def handle_target_position_command(self, *arg):
        if arg[0]:
            self.target_position = int(arg[0])
            self.target_position_lock.ensure_released()

    def handle_current_position_command(self, *arg):
        if arg[0]:
            self.current_position = int(arg[0])
            self.current_position_lock.ensure_released()
