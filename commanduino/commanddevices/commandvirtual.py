from .commanddevice import CommandDevice

import logging

module_logger = logging.getLogger(__name__)


class CommandVirtual(CommandDevice):
    """
    Virtual omnipotent device.
    """

    def __init__(self):
        CommandDevice.__init__(self)

    def disable_acceleration(self):
        pass

    def disable_revert_switch(self):
        pass

    def enable_acceleration(self):
        pass

    def enable_revert_switch(self):
        pass

    def get_celsius(self):
        pass

    def get_current_position(self):
        return 0

    def get_humidity(self):
        pass

    def get_state(self):
        pass

    def high(self):
        pass

    def home(self, wait=True):
        pass

    def is_moving(self):
        return False

    def low(self):
        pass

    def move(self, position=[], wait=True):
        pass

    def move_to(self, position=[], wait=True):
        pass

    def set_acceleration(self, steps_per_second_per_second):
        pass

    def set_angle(self, angle):
        pass

    def set_homing_speed(self, steps_per_second):
        pass

    def set_level(self, level):
        pass

    def set_limit(self, minimum=0, maximum=180):
        pass

    def set_max_speed(self, steps_per_second):
        pass

    def set_pwm_value(self, value):
        pass

    def set_running_speed(self, steps_per_second):
        pass

    def set_speed(self, steps_per_second):
        pass

    def stop(self):
        pass

    def wait_until_idle(self):
        pass
