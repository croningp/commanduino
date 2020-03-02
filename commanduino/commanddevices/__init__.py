"""
Custom package for managing different Arduino devices to be used in the Commanduino Library.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""

from .register import add_to_bonjour_register

# default
from .commanddevice import CommandDevice
add_to_bonjour_register('TEMPLATE', CommandDevice)

# digital
from .commanddigitalread import CommandDigitalRead
add_to_bonjour_register('DIGITALREAD', CommandDigitalRead)

from .commanddigitalwrite import CommandDigitalWrite
add_to_bonjour_register('DIGITALWRITE', CommandDigitalWrite)

# analog
from .commandanalogread import CommandAnalogRead
add_to_bonjour_register('ANALOGREAD', CommandAnalogRead)

from .commandanalogwrite import CommandAnalogWrite
add_to_bonjour_register('ANALOGWRITE', CommandAnalogWrite)

# servo
from .commandservo import CommandServo
add_to_bonjour_register('SERVO', CommandServo)

# commandlinearaccelstepper
from .commandlinearaccelstepper import CommandLinearAccelStepper
add_to_bonjour_register('LINEARACCELSTEPPER', CommandLinearAccelStepper)

# commandaccelstepper
from .commandaccelstepper import CommandAccelStepper
add_to_bonjour_register('ACCELSTEPPER', CommandAccelStepper)

# Temperature sensors SHT1X
from .commandsht1x import CommandSHT1X
add_to_bonjour_register('SHT1X', CommandSHT1X)

# Temperature sensors SHT31
from .commandsht31 import CommandSHT31
add_to_bonjour_register('SHT31', CommandSHT31)

# Dallas temperature sensors
from .commanddallas import CommandDallas
add_to_bonjour_register('DALLAS', CommandDallas)

# virtual
from .commandvirtual import CommandVirtual

# automated way, seems to only works in develop mode :(

# import os
# import glob
# import inspect
#
# from register import DeviceBonjourRegisterError
#
# path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# submodules = glob.glob(os.path.join(path, '*.py'))
#
# for mod_name in submodules:
#     mod_name = os.path.basename(mod_name).replace('.py', '')
#     if not mod_name.startswith('__') and not mod_name == 'register':
#         mod = __import__(mod_name, globals(), locals())
#         if hasattr(mod, 'BONJOUR_ID') and hasattr(mod, 'CLASS_NAME'):
#             bonjour_id = getattr(mod, 'BONJOUR_ID')
#             class_name = getattr(mod, 'CLASS_NAME')
#             constructor = getattr(mod, class_name)
#             add_to_bonjour_register(bonjour_id, constructor)
#         else:
#             raise DeviceBonjourRegisterError(mod_name)
