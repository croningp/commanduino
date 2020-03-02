# Commanduino Library

Link to the documentation: [Commanduino](https://croningp.github.io/commanduino/index.html)

This is the commanduino library for controlling Arduino hardware via a python interface. By using the [Arduino-CommandTools](https://github.com/croningp/Arduino-CommandTools) and [Arduino-CommandHandler](https://github.com/croningp/Arduino-CommandHandler) libraries in conjunction with commanduino, you can essentially control any supported Arduino device through Python.

## How This Library Works
The commanduino library is a python library which is used to communicate with Arduino devices via Python, as opposed to hardcoding the desired behaviour onto the Arduino itself. This works by using the [Arduino-CommandTools](https://github.com/croningp/Arduino-CommandTools) and [Arduino-CommandHandler](https://github.com/croningp/Arduino-CommandHandler) libraries. Commanduino acts as a friendlier "front-end" for the devices.

### Arduino-CommandTools Library
This library is responsible for the code controlling each Arduino device. A CommandManger within the library controls the initialisation of the devices. To achieve total control of the device, the arduino functionality (the commands you would enter in an Arduino sketch, for example) are wrapped in methods which are called when specific commands are sent (These are specific to each device and are implemented in the library). The actual Arduino sketch will instantiate a CommandManager object which will manage the incoming/outgoing commands.  These commands are handled by the Arduino-CommandHandler library which manages the communications between the Arduino device and the controlling computer via serial communication.  
To test the devices, the commands can be sent to the device via the Serial Monitor present within the Arduino IDE. 

```
Serial Monitor Test
<Device ID>,<Command>,<Value>;

E.g.
stepper1,M,2000;

This would move a stepper motor with ID "stepper1" 2000 steps.
```

### Commanduino
Commanduino is a Python interface for this interaction. It uses its own version of the CommandManager and CommandHandler, which initialise and communicate with the Arduino hardware via the Arduino-CommandTools & Arduino-CommandHandler libraries. Each Arduino device is implemented in python with commands and functions that mirror those in the Arduino-CommandTools. This allows python to directly communicate with the hardware. The commanduino implementation of the CommandManager deals with the communications to the hardware. To use the CommandManager, one simply needs to create a config file with the device information and instantiate a CommandManager object which then reads the setup information from the config file. This will give you control of the device in Python. See the [Examples](#Using The Library) section for more information.

### Hierarchical Design of Commanduino
The following diagram shows the design of Commanduino, highlighting the layers of communication.

![Alt text](https://cloud.githubusercontent.com/assets/13821621/20561408/6886aa92-b176-11e6-8987-4d69ce578e6a.png "Commanduino Hierarchy")

Links to relevant GitHub Repositories:
* Python:
	* [Command Handler/Serial Command Handler](https://github.com/croningp/commanduino/blob/master/commanduino/commandhandler.py)
	* [Command Manager](https://github.com/croningp/commanduino/blob/master/commanduino/commandmanager.py)
	* [Command Devices](https://github.com/croningp/commanduino/tree/master/commanduino/commanddevices)

* Arduino:
	* [Command Handler](https://github.com/croningp/Arduino-CommandHandler)
	* [Command Manager](https://github.com/croningp/Arduino-CommandTools/tree/master/CommandManager)
	* [Command Devices](https://github.com/croningp/Arduino-CommandTools)

## Tutorial
The following will serve as a tutorial on how to use this library. An example is provided which will demonstrate using the library with a supported device (Servo Motor).

### List of Currently Supported Devices
* AccelStepper Motor
* Analog Read capabilities
* Analog Write capabilities
* Digital Read capabilities
* Digital Write capabilities
* Linear Accel Stepper Actuator
* SHT1X Temperature Sensor
* SHT31 Temperature Sensor
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
Using this library is extremely simple! This example will demonstrate the use of a Servo motor.
All Demo files (either Arduino or Python) have an equivalent demo file in their respective counterpart (either Python or Arduino).

* First, create an Arduino sketch for your device (Demo can be found at `File > Examples > CommandServo > Demo`):

```cpp
#include <CommandHandler.h>
#include <CommandManager.h>
CommandManager cmdMng; //Create a CommandManager

//Install this library from Arduino's IDE
#include <Servo.h>

#include <CommandServo.h>
CommandServo cmdServo1(9); //The parameter is the Pin number which you plug the device into

void setup()
{
  Serial.begin(115200);

  cmdServo1.registerToCommandManager(cmdMng, "S1"); //Register the Device to the CommandManager


  cmdMng.init(); //Initialise the Manager
}

void loop()
{
  cmdMng.update();
}

```

* Then, load this sketch onto the Arduino Board

* Create a json config file containing the information of the device:
	* The `"ios"` represents the USB auto-detection of the Arduino Board
	* `/dev/tty.usbmodem1411` represents a Mac USB port
	* `/dev/ttyACM0/1/2 etc.` represents the Linux USB ports
	* `COM[number]` represents the Windows USB ports
	* The library will automatically search these ports for connected Arduino devices

```json
{
  "ios" : [
    {
      "port": "/dev/tty.usbmodem1411"
    },
    {
      "port": "/dev/ttyACM0"
    },
    {
      "port": "/dev/ttyACM1"
    },
    {
      "port": "/dev/ttyACM2"
    }
  ],
  "devices": {
    "servo1": {
      "command_id": "S1"
    }
  }
}
```

* Next, just import the commanduino library and read the config file. You're now ready to access the methods of the device!

```python

"""
This script reads the information provided by the Config file and creates a CommandManager with this information. This sets up the device on both the Arduino side and Python side which allows you to control it.
"""
import time

from commanduino import CommandManager

cmdMng = CommandManager.from_configfile('./demo.json')


for i in range(2):
    cmdMng.servo1.set_angle(60)
    print(cmdMng.servo1.get_angle())
    time.sleep(1)

    cmdMng.servo1.set_angle(120)
    print(cmdMng.servo1.get_angle())
    time.sleep(1)

```

This script in particular will set the angle of the Servo motor to 60 degrees, wait for 1 second then set the angle to 120 degrees.
When the script calls `cmdMng.servo1.set_angle(60)`, it is actually sending the command `S1,SA,60;` to the Arduino device which is then processed by the CommandHandler to obtain the desired movement.

That's all there is to it!

## Authors

[Jonathan Grizou](http://www.chem.gla.ac.uk/cronin/members/Jonathan/), [Graham Keenan](https://github.com/ShinRa26) and [Dario Cambie](http://www.chem.gla.ac.uk/cronin/members/DCambie/) while working in the [Cronin Group](http://www.chem.gla.ac.uk/cronin/).

## License

[![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl.html)
