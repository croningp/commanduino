from commandruino.commandhandler import SerialCommandHandler


def defaultPrint(cmd):
    print cmd

cmdHdl = SerialCommandHandler('/dev/cu.usbmodem1411')
cmdHdl.addDefaultHandler(defaultPrint)
cmdHdl.start()

quit = False
while not quit:
    msg = raw_input()
    if msg == "QUIT":
        isRunning = False
        quit = True
    else:
        cmdHdl.write(msg)

cmdHdl.stop()
cmdHdl.join()
