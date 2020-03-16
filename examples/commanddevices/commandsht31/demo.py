import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandsht31/demo.json')

for i in range(10):
    C = cmdMng.sht31.get_celsius()
    H = cmdMng.sht31.get_humidity()
    print('###')
    print('Temperature = {} C'.format(C))
    print('Humidity = {}%'.format(H))
    time.sleep(1)
