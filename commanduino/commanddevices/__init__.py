import os
import glob
import inspect

from register import add_to_bonjour_register
from register import DeviceBonjourRegisterError

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
submodules = glob.glob(os.path.join(path, '*.py'))

for mod_name in submodules:
    mod_name = os.path.basename(mod_name).replace('.py', '')
    if not mod_name.startswith('__') and not mod_name == 'register':
        mod = __import__(mod_name, globals(), locals())
        if hasattr(mod, 'BONJOUR_ID') and hasattr(mod, 'CLASS_NAME'):
            bonjour_id = getattr(mod, 'BONJOUR_ID')
            class_name = getattr(mod, 'CLASS_NAME')
            constructor = getattr(mod, class_name)
            add_to_bonjour_register(bonjour_id, constructor)
        else:
            raise DeviceBonjourRegisterError(mod_name)
