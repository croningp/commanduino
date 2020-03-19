#!/usr/bin/python
# coding: utf-8

import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commanddallas/demo.json')


for i in range(10):
    C = cmdMng.D1.get_celsius()
    print("Temperature = {}°C".format(C))


if __name__ == '__main__':
    pass
