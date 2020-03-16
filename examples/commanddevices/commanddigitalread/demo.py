import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)


cmdMng = CommandManager.from_configfile('./examples/commanddevices/commanddigitalread/demo.json')


for i in range(10):
    print(cmdMng.D1.get_state())
    time.sleep(1)
