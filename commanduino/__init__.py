"""
Custom library designed to interface with Arduino hardware, allowing for control of the boards via Python.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

from .lock import Lock

from .commandhandler import CommandHandler
from .commandhandler import SerialCommandHandler

from .commandmanager import CommandManager
