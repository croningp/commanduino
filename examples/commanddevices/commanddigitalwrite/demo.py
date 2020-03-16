import time
import logging
logging.basicConfig(level=logging.INFO)


from commanduino import CommandManager

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commanddigitalwrite/demo.json')


for i in range(10):
    cmdMng.D1.high()
    time.sleep(1)
    cmdMng.D1.low()
    time.sleep(1)
