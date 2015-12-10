

class Axis(object):

    def __init__(self, linear_actuator, unit_per_step=1, min_position=0, max_position=float('inf')):
        self.linear_actuator = linear_actuator
        self.unit_per_step = float(unit_per_step)
        self.min_position = float(min_position)
        self.max_position = float(max_position)
        self.initialized = False

    def initialize(self):
        self.home(wait=True)

    def is_initialized(self):
        return self.initialized

    def position_to_step(self, position_in_unit):
        n_steps = position_in_unit / self.unit_per_step
        return int(round(n_steps))

    def step_to_position(self, n_steps):
        return n_steps * self.unit_per_step

    def cast_position(self, position_in_unit):
        casted_position = min(self.max_position, position_in_unit)
        casted_position = max(self.min_position, casted_position)
        return casted_position

    def is_moving(self):
        return self.linear_actuator.is_moving()

    def wait_until_idle(self):
        self.linear_actuator.wait_until_idle()

    def home(self, wait=False):
        self.linear_actuator.home()
        if wait:
            self.wait_until_idle()
        self.initialized = True

    def move_to(self, position_in_unit, wait=False):
        if self.is_initialized():
            if type(position_in_unit) == list:
                position_in_unit = position_in_unit[0]
            position = self.cast_position(position_in_unit)
            n_steps = self.position_to_step(position)
            self.linear_actuator.move_to(n_steps)
            if wait:
                self.wait_until_idle()

    def move(self, position_in_unit, wait=False):
        if self.is_initialized():
            if type(position_in_unit) == list:
                position_in_unit = position_in_unit[0]
            n_steps = self.position_to_step(position_in_unit)
            self.linear_actuator.move(n_steps)
            if wait:
                self.wait_until_idle()

    def get_current_position(self):
        n_steps, _, _ = self.linear_actuator.get_current_position()
        return self.step_to_position(n_steps)

    def stop(self):
        self.linear_actuator.stop()


class MultiAxis(object):

    def __init__(self, *args):
        self.axes = []
        for arg in args:
            self.axes.append(arg)
        self.initialized = False

    def initialize(self):
        self.home(wait=True)

    def is_initialized(self):
        return self.initialized

    def is_moving(self):
        for axis in self.axes:
            if axis.is_moving():
                return True
        return False

    def wait_until_idle(self):
        for axis in self.axes:
            axis.wait_until_idle()

    def home(self, wait=False):
        for axis in self.axes:
            axis.home()
        if wait:
            self.wait_until_idle()
        self.initialized = True

    def move_to(self, position_array_in_unit, wait=False):
        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move_to(position_in_unit)
        if wait:
            self.wait_until_idle()

    def move(self, position_array_in_unit, wait=False):
        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move(position_in_unit)
        if wait:
            self.wait_until_idle()

    def get_current_position(self):
        position = []
        for axis in self.axes:
            position.append(axis.get_current_position())
        return position

    def stop(self):
        for axis in self.axes:
            axis.stop()
