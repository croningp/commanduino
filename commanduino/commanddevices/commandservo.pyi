from .commanddevice import CommandDevice

class CommandServo(CommandDevice):
    def __init__(self, initial_angle: int, min_limit: int, max_limit: int):
        self.initial_angle : int
        self.min_limit : int
        self.max_limit : int
        self.limit : bool

    def set_limit(self, minimum: int, maximum: int) -> bool : ...
    def remove_limit(self) -> None : ...
    def set_angle(self, angle: int) -> None : ...
