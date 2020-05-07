import time
import logging
logging.basicConfig(level=logging.INFO)


from commanduino import CommandManager

cmdMng = CommandManager.from_configfile('./examples/commanddevices/commandaccelstepper/demo.json')


stepper = cmdMng.stepper

print('Setting current position to 0')
stepper.set_current_position(0)

stepper.enable_acceleration()
stepper.set_acceleration(1000)
stepper.set_running_speed(5000)
stepper.set_max_speed(10000)

print('Moving to 20000 with acceleration 1000')
stepper.move_to(20000, wait=True)
print('Moving back to 0 with acceleration 5000')
stepper.set_acceleration(5000)
stepper.move_to(0, wait=True)

#
print('Disabling acceleration')
stepper.disable_acceleration()
stepper.set_max_speed(10000)

#
print('Moving to 20000 with default speed 5000')
stepper.move_to(10000, wait=True)
print('Setting speed to 10000')
stepper.set_running_speed(10000)
print('Moving back to 0')
stepper.move_to(0, wait=True)

print('Current position is {}'.format(stepper.get_current_position()))
