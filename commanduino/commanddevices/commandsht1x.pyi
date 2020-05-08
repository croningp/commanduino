from . import CommandDevice
from ..lock import Lock


class CommandSHT1X(CommandDevice):
    humidity_lock: Lock
    celsius_lock: Lock
    fahrenheit_lock: Lock
    def get_humidity(self) -> float: ...
    def get_celsius(self) -> float: ...
    def get_fahrenheit(self) -> float: ...
