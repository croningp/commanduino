from .commanddevice import CommandDevice

class CommandMCP9600(CommandDevice):
    def __init__(self): ...
    def get_celsius(self) -> float: ...
