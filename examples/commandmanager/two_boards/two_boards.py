from commanduino import CommandManager

import logging
logging.basicConfig(level=logging.INFO)

# in your two board please load the arduino example OF:
# - CommandServo
# - CommandLinearAccelStepper
cmdMng = CommandManager.from_configfile('./examples/commandmanager/two_boards/two_boards.json')

s1 = cmdMng.devices['servo1']
s2 = cmdMng.devices['servo2']
m1 = cmdMng.devices['stepper1']

from commanduino.devices.axis import Axis

a = Axis(m1, 0.1)
