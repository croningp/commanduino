.. _examples:

Examples
********

Here you will find in-depth examples of how to use the Commanduino library.

CommandServo Example
====================
This example focuses on controlling a servo motor attached to an Arduino board via Python.

Below are samples of a .json configuration file and the Python script which controls the motor.

.. note:: This example is for the CommandServo module but other modules can be used this way too, just replace the name!

JSON Configuration file (demo.json)
+++++++++++++++++++++++++++++++++++
This is how to lay out a .json configuration file.

* ios
    This are the I/O port(s) on which the Arduino board is attached to.
    This is dependent on the the port which is set upon uploading code to the Arduino board.
* devices
    These are the names that will be used to communicate with the device in the Python code (e.g. servo1, servo2, etc).

    * command_id
        This is the label which the library uses to identify the device.

    Add as many devices as necessary.

**JSON Configuration file:**

::

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
                "port": "/dev/ttyACM5"
            }
        ],
        "devices": {
            "servo1": {
                "command_id": "S1"
            },
            "servo2": {
                "command_id": "S2"
            }
        }
    }

Python Script (demo.py)
+++++++++++++++++++++++
This is an example of a python script which uses the Commanduino library.

1. First, import the CommandManager module from the commanduino library.
2. Create a CommandManager object, using a .json configuration file to set the parameters.
3. The manager is now initialised and ready for use!
4. You can gain access to the devices through the command manager methods (e.g. cmdMgr.servo1)
5. This will allow access to the control methods for the device (e.g.cmdMgr.servo1.set_angle(60))

Please see the :ref:`command_devices` page for a list of supported devices.

**Python Script Example:**

::

    import time
    import logging
    logging.basicConfig(level=logging.INFO)


    from commanduino import CommandManager

    cmdMng = CommandManager.from_configfile('./demo.json')


    for i in range(2):
        cmdMng.servo1.set_angle(60)
        cmdMng.servo2.set_angle(60)
        print cmdMng.servo1.get_angle()
        print cmdMng.servo2.get_angle()
        time.sleep(1)
        cmdMng.servo1.set_angle(120)
        cmdMng.servo2.set_angle(120)
        print cmdMng.servo1.get_angle()
        print cmdMng.servo2.get_angle()
        time.sleep(1)

.. note:: Insert Examples here similar to the above format!
