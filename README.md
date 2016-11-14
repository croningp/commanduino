# Commanduino Library
This is the commanduino library for controlling Arduino hardware via a python interface. By using the [Arduino-CommandTools](https://github.com/croningp/Arduino-CommandTools) and [Arduino-CommandHandler](https://github.com/croningp/Arduino-CommandHandler) libraries in conjunction with commanduino, you can essentially control any supported Arduino device through Python.

## How This Library Works
MAGIC

## Tutorial
The following will serve as a tutorial on how to use this libary. An example is provided which will demonstrate using the library with a supported device (Servo Motor).

### List of Currently Supported Devices
* AccelStepper Motor
* Analog Read capabilities
* Analog Write capabilities
* Digital Read capabilities
* Digital Write capabilities
* Linear Accel Stepper Actuator
* SHT1X Temperature Sensor
* Servo Motor

This list will be continually updated so keep checking back regularly for more supported devices.

### Installing the Library

```
git clone https://github.com/croningp/commanduino.git
cd commanduino
python setup.py install  # May require the use of sudo
```

Alternatively, if you plan to work on the library itself, use:

```
python setup.py develop
```

This will make a direct link to the folder you are working on.

### Dialout Issues
On initial use, there may be an issue with permissions when trying to communicate over the USB connection on Unix-based OS'. This can be solved by adding the main user to the 'dialout' group on the computer:
```
sudo adduser <username> dialout
```
As this library was develop for Unix-based OS', this issue may not be encountered on Windows.

### Using the Library
MAGIC