import time
import logging
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)


cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandlinearaccelstepper/demo.json')

stepper = cmdMng.stepper

stepper.set_current_position(0)

stepper.enable_acceleration()
stepper.set_acceleration(1000)
stepper.set_max_speed(10000)

print('Moving to 20000 with acceleration 1000')
stepper.move_to(20000, wait=True)

print('Moving back to 0 with acceleration 5000...')
print('Should turn in the opposite direction no?')
stepper.set_acceleration(5000)
stepper.move_to(0, wait=True)


print('Disabling acceleration')
stepper.disable_acceleration()
stepper.set_max_speed(10000)


print('Moving to 20000 with default speed 1000')
stepper.move_to(20000, wait=False)
time.sleep(1)
print('Increasing speed to 10000')
stepper.set_running_speed(10000)
stepper.wait_until_idle()


print('Moving back to 0')
print('Should turn in the opposite direction no?')
print('Speed should still be 10000 no?')
stepper.set_running_speed(10000)
stepper.move_to(0, wait=True)
