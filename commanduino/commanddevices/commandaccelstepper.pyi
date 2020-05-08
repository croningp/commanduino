from . import CommandDevice

class CommandAccelStepper(CommandDevice):
    def __init__(self, speed: float, max_speed: float, acceleration: float, enabled_acceleration: bool = True,
                 reverted_direction: bool = False): ...
    def init(self) -> None: ...
    def set_all_params(self) -> None: ...
    def apply_reverted_direction(self, value: float): ...
    @property
    def is_moving(self) -> bool: ...
    def wait_until_idle(self) -> None: ...
    def set_current_position(self, steps: float) -> None: ...
    def _set_speed(self, steps_per_sec: float) -> None: ...
    def set_running_speed(self, steps_per_sec: float) -> None: ...
    def set_max_speed(self, steps_per_sec: float) -> None: ...
    def set_acceleration(self, steps_per_sec_per_sec: float) -> None: ...
    def enable_acceleration(self) -> None: ...
    def disable_acceleration(self) -> None: ...
    def move_to(self, steps: int, wait: bool = True) -> None: ...
    def move(self, steps: int, wait: bool = True) -> None: ...
    def stop(self, wait: bool = True) -> None: ...