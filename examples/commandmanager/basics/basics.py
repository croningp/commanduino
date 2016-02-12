from commanduino import CommandManager

import logging
logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./basics.json')

quit = False
while not quit:
    msg = raw_input()
    if msg == "QUIT":
        isRunning = False
        quit = True
    elif msg == "REQUEST":
        print(cmdMng.devices['servo1'].get_angle())
    else:
        cmdMng.serialcommandhandlers[0].write(msg)
