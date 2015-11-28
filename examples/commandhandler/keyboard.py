import time

from commandruino.commandhandler import KeyboardCommandHandler


def printDefault(cmd):
    print '\r' + cmd

cmdHdl = KeyboardCommandHandler()
cmdHdl.addDefaultHandler(printDefault)
cmdHdl.start()

while cmdHdl.is_alive():
    time.sleep(1)

cmdHdl.join()
