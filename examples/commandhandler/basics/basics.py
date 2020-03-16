from commanduino.commandhandler import (SerialCommandHandler, TCPIPCommandHandler)

def defaultPrint(cmd):
    print(cmd)

config_tcpip = {"port":"5000", "address":"192.168.1.80"}
config_serial = {"port":"COM3"}

# Uncomment and use one of the lines below

# Create with default constructor
#cmdHdl = SerialCommandHandler(port="COM3")
cmdHdl = TCPIPCommandHandler(port="5000", address="192.168.1.80")
# Create from configuration dictionary
#cmdHdl = SerialCommandHandler.from_config(config_serial)
#cmdHdl = TCPIPCommandHandler.from_config(config_tcpip)

cmdHdl.start()

q = False
while not q:
    msg = input()
    if msg == "QUIT":
        isRunning = False
        q = True
    else:
        cmdHdl.write(msg)

cmdHdl.stop()
cmdHdl.join()
