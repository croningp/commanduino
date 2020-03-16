import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandservo/demo.json')


for i in range(2):
    cmdMng.servo1.set_angle(60)
    cmdMng.servo2.set_angle(60)
    print(cmdMng.servo1.get_angle())
    print(cmdMng.servo2.get_angle())
    time.sleep(1)
    cmdMng.servo1.set_angle(120)
    cmdMng.servo2.set_angle(120)
    print(cmdMng.servo1.get_angle())
    print(cmdMng.servo2.get_angle())
    time.sleep(1)
