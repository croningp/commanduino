"""
.. module:: CommandTCS34725
   :platform: Unix
   :synopsis: Represents a MAX31865 PT100 RTD Temperature Sensor Amplifier.
.. moduleauthor:: Alex Hammer <2423935H@student.gla.ac.uk>
"""

import time

from .commanddevice import CommandDevice

# Bonjour Information
BONJOUR_ID = 'MAX31865'
CLASS_NAME = 'CommandMAX31865'

# Constants
RREF = 430.0 # 430.0 for PT100 and 4300.0 for PT1000
RNOMINAL = 100.0 # 100.0 for PT100 and 1000.0 for PT1000
WIRES = 3 # Can be 2, 3 or 4 depending on number of wires used in setup
CSPIN = 10 # CS pin used for hardware SPI connection, can be any digital pin


# Incoming
CMD_READ_TEMP = 'R'
CMD_REPLY_HEADER = 'C'
CMD_INITIALIZE = 'Z'
CMD_INITIALIZE_HEADER = 'E'

# Outgoing

class CommandMAX31865(CommandDevice):
    """
    MAX31865 PT100 RTD Temperature Sensor Amplifier
    """
    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

        self._rref = RREF
        self._rnominal = RNOMINAL

    def register_all_requests(self):
        """Registers all requests."""
        self.register_request(
            CMD_READ_TEMP,
            CMD_REPLY_HEADER,
            'temp',
            self.handle_get_temp
        )
        self.register_request(
            CMD_INITIALIZE,
            CMD_INITIALIZE_HEADER,
            'initialization_code',
            self.handle_initialize,
            timeout=1.2,
        )

    def handle_initialize(self, *arg):
        """ Handles the sensor initialization command. """
        if arg[0]:
            self.initialization_code = int(arg[0])
            self.initialization_code_lock.ensure_released()

    def init(self, 
            rref=RREF,
            rnominal=RNOMINAL,
            cspin=CSPIN,
            wires=WIRES,
            ):
        """ Initializes the sensor. 
        
        Refer to self.initialization_code for checking if the initialization was successful.
        <sensor>.initialization_code is None - the device wasn't initialized, call get_initialization_code()
        <sensor>.initialization_code == 1 - the device is found and the communication was established successfully
        <sensor>.initialization_code == 0 - the device was not found or the communication cannot be established, please
            check the device datasheet for possible reasons
        Call get_initialization_code() to try again.
        """

        self.get_initialization_code()

        if self.initialization_code != 1:
            self.logger.error("Unable to connect to sensor!")
        
        # wait for sensor to stabilize
        time.sleep(1)

    def handle_get_temp(self, *arg):
        """ Handles the temp read command. """
        if arg[0]:
            self.temp = (str(arg[0]), float(arg[1]))
            self.temp_lock.ensure_released()
