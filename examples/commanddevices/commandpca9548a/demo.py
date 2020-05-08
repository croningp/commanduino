import random
import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

cmdMng = CommandManager.from_configfile('demo.json')

for _ in range(3):
    mask = cmdMng.i2c_mux.get_channels()
    assert 0 <= mask <= 255
    print(f"Got the following channels from device: {format(int(mask), '#010b')[2:]}")
    time.sleep(1)
    next_mask = random.choice(range(256))
    cmdMng.i2c_mux.set_channels(next_mask)
    print(f"Set the channels to {format(int(next_mask), '#010b')[2:]}")

