"""
An example module to work with the TCS34725 RGB sensor as Arduino device.
"""

import time
import logging
import os
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

HERE = os.path.abspath(os.path.dirname(__file__))
DEMO = os.path.join(HERE, 'demo.json')

cmdMng = CommandManager.from_configfile(DEMO)

# Upon instantiation, initialization code can be used to check if the sensor is actually attached
# <sensor>.initialization_code is None - the device wasn't initialized, call get_initialization_code()
# <sensor>.initialization_code == 1 - the device is found and the communication was established successfully
# <sensor>.initialization_code == 0 - the device was not found or the communication cannot be established, please
#   check the device datasheet for possible reasons
#
# Call get_initialization_code() to try again.

# Below is an example code for a check
class SensorError(Exception):
    """ Generic sensor error. """
if cmdMng.demo.initialization_code is not None and cmdMng.demo.initialization_code == 0:
    raise SensorError("Sensor is not connected!")

for i in range(3):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))

print('INTEGRATION TIME 700')
cmdMng.demo.set_integration_time(700)
for i in range(3):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))

print('GAIN 16')
cmdMng.demo.set_gain(16)
for i in range(3):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))
