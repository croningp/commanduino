"""

.. module:: CommandMAX31865
   :platform: Windows
   :synopsis: Represents a MAX31865 PT100 RTD Temperature Sensor Amplifier.

.. moduleauthor:: Alex Hammer <2423935H@student.gla.ac.uk>

"""

import time

from .commanddevice import CommandDevice

# Bonjour Information
BONJOUR_ID = 'MAX31865'
CLASS_NAME = 'CommandMAX31865'

# Incoming
CMD_READ_TEMP = 'R'
CMD_READ_ERROR = 'R'
CMD_REPLY_HEADER = 'C'
CMD_INITIALIZE = 'Z'
CMD_INITIALIZE_HEADER = 'E'


class CommandMAX31865(CommandDevice):
    """
    MAX31865 Arduino device.
    
    Implementation based on Adafruit RTD amplifier board.

    Base:
        CommandDevice
    """
    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()


    def register_all_requests(self):
        """ Registers all requests. """
        self.register_request(
            CMD_READ_TEMP,
            CMD_REPLY_HEADER,
            'temp',
            self.handle_get_temp
        )
        self.register_request(
            CMD_READ_ERROR,
            CMD_REPLY_HEADER,
            'error_code',
            self.handle_get_error_code
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

    def init(self):
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
            self.temp = float(arg[1])
            self.temp_lock.ensure_released()

    def handle_get_error_code(self, *arg):
        """ Handles the fault code read command. """
        if arg[0]:
            self.error_code = int(arg[0])
            self.error_code_lock.ensure_released()
