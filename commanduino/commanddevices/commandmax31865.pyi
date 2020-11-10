<<<<<<< HEAD
from typing import Tuple

from .commanddevice import CommandDevice


class CommandTCS34725(CommandDevice):
    def initialization_code(self) -> None: ...
    def get_temp(self) -> float: ...
    def get_error_code(self) -> int: ...
=======
from . import CommandDevice

class CommandMAX31865(CommandDevice):
    def get_temp(self) -> Tuple[str, float]: ...
>>>>>>> 326808ff6d79e3dec0c0ce79633bee54527586c2
