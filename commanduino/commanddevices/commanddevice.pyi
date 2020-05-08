import logging
from typing import Dict
from ..commandhandler import GenericCommandHandler

class CommandDevice:
    logger: logging.Logger
    cmdHdl: GenericCommandHandler
    @classmethod
    def from_config(cls, config: Dict) -> CommandDevice: ...
