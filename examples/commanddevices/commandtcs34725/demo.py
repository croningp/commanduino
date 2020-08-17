import time
import logging
import os
from commanduino import CommandManager

logging.basicConfig(level=logging.INFO)

HERE = os.path.abspath(os.path.dirname(__file__))
DEMO = os.path.join(HERE, 'demo.json')

cmdMng = CommandManager.from_configfile(DEMO)

# print(cmdMng.__dict__)

for i in range(10):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))

print('INTEGRATION TIME 700')
cmdMng.demo.set_integration_time(700)
for i in range(10):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))

print('GAIN 16')
cmdMng.demo.set_gain(16)
for i in range(10):
    start_time = time.time()
    C = cmdMng.demo.get_rgbc()
    end_time = time.time()
    print("RGBC = R {0}, G {1}, B {2}, C {3}, time {4}".format(*C, end_time-start_time))

if __name__ == '__main__':
    pass
