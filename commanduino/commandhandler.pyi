from typing import Dict

class CommandHandler:
    @classmethod
    def from_config(cls, config: Dict) -> CommandHandler: ...
