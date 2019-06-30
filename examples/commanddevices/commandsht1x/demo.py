import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./demo.json')

for i in range(10):
    F = cmdMng.sht15.get_fahrenheit()
    C = cmdMng.sht15.get_celsius()
    H = cmdMng.sht15.get_humidity()
    print('###')
    print('Temperature = {} F  /  {} C'.format(F, C))
    print('Humidity = {}%'.format(H))
    time.sleep(1)
