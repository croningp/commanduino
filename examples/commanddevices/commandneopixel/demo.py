import time
from commanduino import CommandManager

mgr = CommandManager.from_configfile("./demo.json")

mgr.NPX.on()
time.sleep(5)
mgr.NPX.set_color(255, 0, 0)
time.sleep(5)
mgr.NPX.set_color(0, 255, 0)
time.sleep(5)
mgr.NPX.set_color(0, 0, 255)
time.sleep(5)
mgr.off()
time.sleep(2)
mgr.NPX.set_color(255, 255, 255)
time.sleep(2)

for i in range(1, 256, 10):
    mgr.NPX.set_brightness(i)
    time.sleep(1)

mgr.NPX.set_brightness(255)
time.sleep(1)
mgr.NPX.off()
