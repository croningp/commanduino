import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandanalogread/demo.json')


for i in range(10):
    print(cmdMng.A1.get_level())
    time.sleep(1)
