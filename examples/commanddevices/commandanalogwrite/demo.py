import time
import logging
logging.basicConfig(level=logging.INFO)


from commanduino import CommandManager

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandanalogwrite/demo.json')


for i in range(10):
    cmdMng.A1.set_pwm_value(255)
    time.sleep(1)
    cmdMng.A1.set_pwm_value(0)
    time.sleep(1)
    cmdMng.A1.set_pwm_value(50)
    time.sleep(1)
    cmdMng.A1.set_pwm_value(0)
    time.sleep(1)
