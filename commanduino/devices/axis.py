"""

.. module:: Axis
   :platform: Unix
   :synopsis: Represents an Axis which devices can move along

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

import logging


class Axis(object):
    """
    Represents a singular Axis which devices can move along.

    Args:
        linear_actuator: The linear actuator which moves along the axis.

        unit_per_step Union(int, float): Amount of units to move per step, default set to 1

        min_position Union(int, float): Minimum position of the axis (in unit), default set
                            to 0

        max_position Union(int, float, str): The maximum position of the axis (in unit), cast to
                            (float)

    """

    def __init__(self, linear_actuator, unit_per_step=1, min_position=0,
                 max_position=float('inf')):
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self.linear_actuator = linear_actuator
        self.unit_per_step = float(unit_per_step)
        self.min_position = float(min_position)
        self.max_position = float(max_position)
        self.initialized = False

    def initialize(self):
        """
        Initialises the axis.
        """

        self.home(wait=True)

    def is_initialized(self):
        """
        Check for initialisation.

        Returns:
            self.initialized (bool): Initialisation status

        """

        return self.initialized

    def position_to_step(self, position_in_unit):
        """
        Converts position to steps.

        Args:
            position_in_unit (int): Position in Units.

        Returns:
            n_steps (int): Number of steps.

        """

        n_steps = position_in_unit / self.unit_per_step
        return int(round(n_steps))

    def step_to_position(self, n_steps):
        """
        Converts steps to position.

        Args:
            n_steps (int): Number of steps.

        Returns:
            n_steps * units_per_step

        """

        return n_steps * self.unit_per_step

    def cast_position(self, position_in_unit):
        """
        Casts the position on the axis.

        Args:
            position_in_unit (int): Position in units.

        Returns:
            casted_position (int): The casted position.

        """

        casted_position = min(self.max_position, position_in_unit)
        casted_position = max(self.min_position, casted_position)
        if casted_position != position_in_unit:
            self.logger.warning("The position requested ({}) is outside the axis boundary!".format(position_in_unit))
        return casted_position

    def is_moving(self):
        """
        Check for axis movement.

        Returns:
            self.linear_actuator.is_moving (bool): The actuator movement
            status.

        """

        return self.linear_actuator.is_moving()

    def wait_until_idle(self):
        """
        Waits until the linear actuator is idle.
        """

        self.linear_actuator.wait_until_idle()

    def home(self, wait=True):
        """
        Returns the actuator to the home position.

        Args:
            wait (bool): Wait until the actuator is idle, default set to True

        """

        self.linear_actuator.home(wait=wait)
        self.initialized = True

    def move_to(self, position_in_unit, wait=True, force=False):
        """
        Moves the linear actuator to a set position.

        Args:
            position_in_unit (Union(int, list)): Position to move to.

            wait (bool): Wait until the actuator is idle, default set to True.

            force (bool): Force the movement, default set to False.

        """

        if self.is_initialized() or force:
            if type(position_in_unit) == list:
                position_in_unit = position_in_unit[0]
            position = self.cast_position(position_in_unit)
            n_steps = self.position_to_step(position)
            self.linear_actuator.move_to(n_steps, wait=wait)

    def move(self, delta_position_in_unit, wait=True, force=False):
        """
        Moves the linear actuator.

        Args:
            delta_position_in_unit (int): The amount to move.

            wait (bool): Wait until the linear actuator is idle, default set to
                         True.

            force (bool):Force the movement, default set to False.

        """

        current_position = self.get_current_position()
        self.move_to(current_position + delta_position_in_unit, wait=wait,
                     force=force)

    def get_current_position(self):
        """
        Gets the current position on the axis.

        Returns:
            self.step_to_position (int): THe position of the linear actuator.

        """

        n_steps = self.linear_actuator.get_current_position()
        return self.step_to_position(n_steps)

    def get_switch_state(self):
        """
        Gets the switch state of the linear actuator.

        Returns:
            The switch state of the linear actuator.

        """

        return self.linear_actuator.get_switch_state()

    def stop(self):
        """
        Stops the linear actuator.
        """
        self.linear_actuator.stop()


class MultiAxis(object):
    """
    Represents a collection of Axis objects which device can move along.

    Args:
        *args: Variable argument list.

    """

    def __init__(self, *args):
        self.axes = []
        for arg in args:
            self.axes.append(arg)
        self.initialized = False

    def initialize(self):
        """
        Initialises the set of axes.
        """
        self.home(wait=True)

    def is_initialized(self):
        """
        Gets the initialisation status of the devices.

        Returns:
            self.initialised (bool): The initialisation status.

        """

        return self.initialized

    def is_moving(self):
        """
        Check for movement along the axes.

        Returns:
            True (bool): The axes are moving.

            False (bool): The axes are not moving.

        """

        for axis in self.axes:
            if axis.is_moving():
                return True
        return False

    def wait_until_idle(self):
        """
        Waits until the axes are idle.
        """
        for axis in self.axes:
            axis.wait_until_idle()

    def home(self, wait=True):
        """
        Returns the axes to their home position.

        Args:
            wait (bool): Wait until the axes are idle, default set to True.

        """

        for axis in self.axes:
            axis.home(wait=False)
        if wait:
            self.wait_until_idle()
        self.initialized = True

    def move_to(self, position_array_in_unit, wait=True, force=False):
        """
        Moves the axes to a set position.

        Args:
            position_array_in_unit (Union(int, tuple)): The position to move to.

            wait (bool): Wait until the axes are idle, default set to True.

            force (bool): Force the movement of the axes, default se tto False.

        """

        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move_to(position_in_unit, wait=False, force=force)
        if wait:
            self.wait_until_idle()

    def move(self, position_array_in_unit, wait=True, force=False):
        """
        Moves the axes.

        Args:
            position_array_in_unit (list): The amount to move.

            wait (bool): Wait until the axes are idle, default set to True.

            force (bool): Force the movement of the axes, default set to False.

        """

        for i, position_in_unit in enumerate(position_array_in_unit):
            self.axes[i].move(position_in_unit, wait=False, force=force)
        if wait:
            self.wait_until_idle()

    def get_current_position(self):
        """
        Gets the current position of the axes.

        Returns:
            position (List): List of the positions.

        """

        position = []
        for axis in self.axes:
            position.append(axis.get_current_position())
        return position

    def get_switch_state(self):
        """
        Gets the switch state of the axes.

        Returns:
            switch_state (List): List of the switch states.

        """

        switch_state = []
        for axis in self.axes:
            switch_state.append(axis.get_switch_state())
        return switch_state

    def stop(self):
        """
        Stops all movement in the axes.
        """

        for axis in self.axes:
            axis.stop()
