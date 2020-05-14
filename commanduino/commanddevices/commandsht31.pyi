from . import CommandDevice
from ..lock import Lock


class CommandSHT31(CommandDevice):
    humidity_lock: Lock
    celsius_lock: Lock
    def get_humidity(self) -> float: ...
    def get_celsius(self) -> float: ...