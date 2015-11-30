from commandruino import CommandManager

import logging
logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('./two_boards.json')

s1 = cmdMng.devices['servo1']
s2 = cmdMng.devices['servo2']
m1 = cmdMng.devices['stepper1']

# quit = False
# while not quit:
#     msg = raw_input()
#     if msg == "QUIT":
#         isRunning = False
#         quit = True
#     elif msg == "REQUEST":
#         print(cmdMng.devices['servo1'].get_angle())
#     else:
#         cmdMng.serialcommandhandlers[0].write(msg)
