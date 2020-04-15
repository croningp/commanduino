from commanduino import CommandManager

import logging
logging.basicConfig(level=logging.INFO)

#cmdMng = CommandManager.from_configfile('./examples/commandmanager/basics/basics_serial.json')
cmdMng = CommandManager.from_configfile('./examples/commandmanager/basics/basics_tcpip.json')


p1, p2, p3 = True, True, True
while True:
    msg = input()
    if msg == "QUIT":
        break
    elif msg == "P1":
        # Devices can be accessed through devices dictionary
        cmdMng.devices['pin1'].set_level(int(p1))
        # Invert next state for this pin
        p1 = not p1
    elif msg == "P2":
        # Or directly as a CommandManager attribute
        cmdMng.pin2.set_level(int(p2))
        p2 = not p2
    elif msg == "P3":
        if p3 is True:
            cmdMng.pin3.high()
        else:
            cmdMng.pin3.low()
        p3 = not p3