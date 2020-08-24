from . import CommandDevice
from ..lock import Lock


class CommandBME280(CommandDevice):
    pressure_lock: Lock
    temperature_lock: Lock
    humidity_lock: Lock
    def get_pressure(self) -> float: ...
    def get_temperature(self) -> float: ...
    def get_humidity(self) -> float: ...
