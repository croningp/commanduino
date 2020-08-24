import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandbme280/demo.json')

for i in range(10):
    P = cmdMng.bme280.get_pressure()
    T = cmdMng.bme280.get_temperature()
    H = cmdMng.bme280.get_humidity()
    print('###')
    print('Pressure = {} Pascals'.format(P))
    print('Temperature = {} ºC'.format(T))
    print('Humidity = {}%'.format(H))
    time.sleep(1)
