Indoor climate logger 
---------------------

- for microcontrollers running CircuitPython

- for MS-Windows PCs using CPython

- for Linux/RaspberryPi using CPython


 and the Adafruit Blinka module
 ===============================

Work-in progress, Software runs, Readme is unfinished. See instructions in code.
-------------------------------------------

This Python script also uses the Linux kernel driver for temperature readings. 

The 1-Wire bus enables multiple temperature sensors on a single long cable.

The Linux kernel auto-discovers 1-Wire temperature sensors on startup.

You can connect different types of sensors to the same bus. The kernel 

supports 1-Wire sensor types DS18S20, DS1822, DS18B20,  DS28EA00,

MAX31850, and DS1825. The latter two read type K thermocouples,

whereas the others are semiconductor sensors.

The script writes a tab separated value formated text file with 

ISO 8601 date and time. This format is compatible with python's pandas 

and plotly packages as well as with spreadsheet processing. 

The script either logs temperature measurements with its own timer.


Notes
-------

1.) 

