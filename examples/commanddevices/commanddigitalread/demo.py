import time
import logging
logging.basicConfig(level=logging.INFO)


from commanduino import CommandManager

cmdMng = CommandManager.from_configfile('./demo.json')


for i in range(10):
    print cmdMng.D1.get_state()
    time.sleep(1)
