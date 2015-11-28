import serial
import threading


class CommandHandler(object):

    def __init__(self, delim=',', term=';'):
        self.delim = delim  # character separating args in a message
        self.term = term  # character ending a message

        self.buffer = ''  # string that will hold the received data

        self.handlers = {}
        self.defaultHandlers = []

        self.cmdHeader = ''

    def processChar(self, aChar):
        if aChar:
            if aChar == self.term:
                self.handle(self.buffer)
                self.buffer = ''
            else:
                self.buffer += aChar

    def processString(self, aString):
        for aChar in aString:
            self.processChar(aChar)

    def processSerial(self, aSerial):
        self.processChar(aSerial.read(1))

    def handle(self, cmd):
        cmd = cmd.strip()
        cmdList = cmd.split(self.delim)
        cmdId = cmdList[0]
        if cmdId in self.handlers:
            for clb in self.handlers[cmdId]:
                clb(*cmdList[1:])  # all args in the command are given to the cllabeck function as arguments
        else:
            for clb in self.defaultHandlers:
                clb(cmd)  # give back what was received

    def addCommand(self, commandStr, callbackFunction):
        if commandStr not in self.handlers:
            self.handlers[commandStr] = []
        if callbackFunction not in self.handlers[commandStr]:
            self.handlers[commandStr].append(callbackFunction)

    def removeCommand(self, commandStr, callbackFunction):
        if commandStr in self.handlers:
            if callbackFunction in self.handlers[commandStr]:
                self.handlers[commandStr].remove(callbackFunction)

    def addDefaultHandler(self, callbackFunction):
        if callbackFunction not in self.defaultHandlers:
            self.defaultHandlers.append(callbackFunction)

    def removeDefaultHandler(self, callbackFunction):
        if callbackFunction in self.defaultHandlers:
            self.defaultHandlers.remove(callbackFunction)

    #
    def setCommandHeader(self, cmdHeader, addDelim=True):
        self.cmdHeader = cmdHeader
        if addDelim:
            self.cmdHeader += self.delim

    def forgeCommand(self, commandStr, *args):
        cmd = self.cmdHeader
        cmd += commandStr
        for arg in args:
            cmd += self.delim
            cmd += str(arg)
        cmd += self.term
        return cmd


class SerialCommandHandler(threading.Thread, CommandHandler):

    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=0.01, delim=',', term=';'):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        CommandHandler.__init__(self, delim, term)

        self.open(port, baudrate, timeout)

    def open(self, port, baudrate, timeout):
        self._serial = serial.Serial(port, baudrate, timeout=timeout)

    def close(self):
        self._serial.close()

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def stop(self):
        self.interrupted.release()

    def run(self):
        self.interrupted.acquire()
        while not self.interrupted.acquire(False):
            self.processSerial(self._serial)
        self.close()

    def send(self, commandStr, *arg):
        self.write(self.forgeCommand(commandStr, *arg))

    def write(self, msg):
        self._serial.write(msg)


try:
    from keyboardinput import KeyboardInput
except ImportError:
    pass


class KeyboardCommandHandler(threading.Thread, CommandHandler):

    def __init__(self, timeout=0.01, delim=',', term=';'):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        CommandHandler.__init__(self, delim, term)

        self.keyinput = KeyboardInput()
        self.timeout = timeout

    def stop(self):
        self.interrupted.release()

    def run(self):
        self.interrupted.acquire()
        self.keyinput.start()
        while not self.interrupted.acquire(False):
            if self.keyinput.is_alive():
                ret = self.keyinput.read(self.timeout)
                if ret:
                    self.processChar(ret)
            else:
                self.stop()

    def send(self, commandStr, *arg):
        self.sendCmdSerial(self._serial, commandStr, *arg)

    def write(self, msg):
        self._serial.write(msg)
