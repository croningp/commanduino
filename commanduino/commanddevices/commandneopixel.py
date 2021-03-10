from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# REgistration protocol information
BONJOUR_ID = 'NEOPIXEL'
CLASS_NAME = 'CommandNeoPixel'

# Commands
CMD_SET_COLOR = "SC"
CMD_SET_BRIGHTNESS = "SB"

def limit_value(value: int) -> int:
    """Limits a value between 0 adn 255

    Args:
        value (int): Value to limit

    Returns:
        int: Limited value
    """

    return max(min(value, 255), 0)

class CommandNeoPixel(CommandDevice):
    """Class representing the AdaFruit NeoPixel device

    Inherits:
        CommandDevice: Base command device
    """

    def __init__(self):
        super().__init__()

        # Initialise an RGB value of pure white
        self.rgb = (255, 255, 255)

    def on(self):
        """Sends the command to set the LED to the given RGB and turn it on
        """
        self.send(CMD_SET_COLOR, *self.rgb)

    def off(self):
        """Sends the command to turn off the LED by setting RGB to (0,0,0)
        """

        self.send(CMD_SET_COLOR, 0, 0, 0)

    def set_color(self, red: int, green: int, blue: int):
        """Sets the RGB value and switches on the LED

        Args:
            red (int): Red value
            green (int): Green value
            blue (int): Blue value
        """

        self.rgb = (limit_value(red), limit_value(green), limit_value(blue))
        self.on()

    def set_brightness(self, brightness: int):
        """Sets the brightness of the LED and sends the command

        Args:
            brightness (int): Brioghtness value (0-255)
        """

        brightness = limit_value(brightness)
        self.send(CMD_SET_BRIGHTNESS, brightness)
