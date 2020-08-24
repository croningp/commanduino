"""

.. module:: CommandTCS34725
   :platform: Unix
   :synopsis: Represents a TCS34725 Arduino Device.

.. moduleauthor:: Artem Leonov <Artem.Leonov@glasgow.ac.uk>

"""

import time

from .commanddevice import CommandDevice

# Bonjour Information
BONJOUR_ID = 'TCS34725'
CLASS_NAME = 'CommandTCS34725'

# Incoming
CMD_READ_RGBC = 'R'
CMD_REPLY_HEADER = 'C'
CMD_INITIALIZE = 'Z'
CMD_INITIALIZE_HEADER = 'E'

# Outgoing
CMD_SET_INTEGRATION_TIME = 'I'
CMD_SET_GAIN = 'G'

# Accepted values
INTEGRATION_TIMES = [2.4, 24, 50, 101, 154, 700]
GAINS = [1, 4, 16, 60]


class CommandTCS34725(CommandDevice):
    """
    TCS34725 Arduino device.
    
    Implementation based on Adafruit #1334 RGB sensor.

    Base:
        CommandDevice
    """
    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

        # value placeholders
        self._integration_time = 0.05 # 50 ms by default
        self._gain = 4 # default

    def register_all_requests(self):
        """ Registers all requests. """
        self.register_request(
            CMD_READ_RGBC,
            CMD_REPLY_HEADER,
            'rgbc',
            self.handle_get_rgbc
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
        time.sleep(self._integration_time * self._gain)

    def handle_get_rgbc(self, *arg):
        """ Handles the rgbc read command. """
        if arg[0]:
            self.rgbc = (int(arg[0]), int(arg[1]), int(arg[2]), int(arg[3]))
            self.rgbc_lock.ensure_released()

    def set_integration_time(self, integration_time):
        """ Sets the sensor integration time.

        Delays the following execution by integration time * gain.

        Args:
            integration_time (float): Integration time for all channels in ms.
                Accepted values - 2.4, 24, 50, 101, 154, 700. If supplied argument is
                not an accepted value - sets to 50 ms by default.
        """
        
        # multiply by 10 to avoid float parsing/calculations
        if integration_time in INTEGRATION_TIMES:
            integration_time *= 10
        
        # setting to 50 ms in case of invalid value
        else:
            self.logger.warning("Invalid integration time given, setting to default 50 ms.")
            integration_time = 500

        self.send(CMD_SET_INTEGRATION_TIME, integration_time)

        # updating placeholder
        self._integration_time = integration_time / 10 / 1000 # get rid of *10 and convert to seconds

        # delay to correctly set up the value
        time.sleep(self._integration_time * self._gain)

    def set_gain(self, gain):
        """ Sets the channels gain.

        Delays the following execution by integration time * gain.

        Args:
            gain (int): Gain for all channels.  
                Accepted values: 1, 4, 16, 60. If supplied argument is not an accepted
                value - sets to 4 by default.
        """

        # setting to default 4 if incorrect value supplied
        if gain not in GAINS:
            self.logger.warning("Invalid gain given, setting to default 4X.")
            gain = 4

        self.send(CMD_SET_GAIN, gain)

        # updating placeholder
        self._gain = gain

        # delay to correctly set up the value
        time.sleep(self._integration_time * self._gain)
