

class Axis(object):

    def __init__(self, linear_actuator, unit_per_step):
        self.linear_actuator = linear_actuator
        self.unit_per_step = float(unit_per_step)

    def position_to_step(self, position_in_unit):
        n_steps = position_in_unit / self.unit_per_step
        return int(round(n_steps))

    def step_to_position(self, n_steps):
        return n_steps * self.unit_per_step

    def is_moving(self):
        return self.linear_actuator.is_moving()

    def wait_until_idle(self):
        self.linear_actuator.wait_until_idle()

    def home(self):
        self.linear_actuator.home()

    def move_to(self, position_in_unit):
        n_steps = self.position_to_step(position_in_unit)
        self.linear_actuator.move_to(n_steps)

    def move(self, position_in_unit):
        n_steps = self.position_to_step(position_in_unit)
        self.linear_actuator.move(n_steps)

    def get_current_position(self):
        n_steps, _, _ = self.linear_actuator.get_current_position()
        return self.step_to_position(n_steps)

    def stop(self):
        self.linear_actuator.stop()


class MultiAxis(object):

    def __init__(self, *args):
        self.axes = []
        for arg in args:
            self.axaxesis.append(arg)

    def is_moving(self):
        for axis in self.axes:
            if axis.is_moving():
                return True
        return False

    def wait_until_idle(self):
        for axis in self.axes:
            axis.wait_until_idle()

    def home(self):
        for axis in self.axes:
            axis.home()

    def move_to(self, position_array_in_unit):
        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move_to(position_in_unit)

    def move(self, position_array_in_unit):
        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move(position_in_unit)

    def get_current_position(self):
        position = []
        for axis in self.axes:
            position.append(axis.get_current_position())

    def stop(self):
        for axis in self.axes:
            axis.stop()
