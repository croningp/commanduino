from commanduino.commandhandler import (SerialCommandHandler, TCPIPCommandHandler)


def defaultPrint(cmd):
    print(cmd)


#cmdHdl = SerialCommandHandler(port="COM3")
cmdHdl = TCPIPCommandHandler(port="5000", address="192.168.1.80")
cmdHdl.start()

q = False
while not quit:
    msg = input()
    if msg == "QUIT":
        isRunning = False
        q = True
    else:
        cmdHdl.write(msg)

cmdHdl.stop()
cmdHdl.join()
