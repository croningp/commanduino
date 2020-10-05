from . import CommandDevice

class CommandMAX31865(CommandDevice):
    def get_temp(self) -> Tuple[str, float]: ...