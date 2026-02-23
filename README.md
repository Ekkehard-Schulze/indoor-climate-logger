Indoor climate logger 
=====================

for

- microcontrollers running CircuitPython

- MS-Windows PCs using CPython

- Linux/RaspberryPi using CPython


For microcontrollers running CircuitPython
------------------------------------------

**you need**

- CircuitPython, this code was developed using version 9.2.1 on RaspberrPi Pico2W and Pico2W
- the /lib folder
- the hardware drivers from the Adafruit library bundle for your CircuitPython version:
  https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases
  adafruit_register, adafruit_tmp117, adafruit_adt7410, 
  adafruit_bme280, adafruit_bme680, 
  adafruit_mlx90614, adafruit_tsl2561,
  adafruit_onewire, adafruit_ds3231, adafruit_ntp
  these go to the /lib folder.
  
  You may omit the drivers for the sensors you do not use.
- indoor-climate-logger.py renamed to code.py, header edited for your desired user settings
- boot.py
- if you want to activate WiFi, edit settings_template.toml with your credentials
  and rename it to settings.toml
  
  **you may like to use**
  - switch_RPiPico_to_USB_read_log_mode.py runs in CPython and renames boot.py to boot.bak on the microcontroller, when 
	plugged to a USB port, even when the filesystem is mounted read-only. After a reset or
	re-plug of the microcontroller, the the files system is mounted read only for the controller,
	and now log data can be copied to the PC. This is required, WiFi is not available or not
	activated.
 
  - switch_RPiPico_to_write_log_mode.py runs in CPython and renames boot.bak to boot.py. For the
    convenience of the developer, it also copies indoor-climate-logger.py to code.py and offers to
	delete indoor-climate-logger.py. After a reset or e-plug of the microcontroller, the the files system 
	is mounted read write for the controller and the controller starts logging data. It is not possible
	to read the growing log file via USB, however in verboose mode the data are also pinted to the
	repl, e. g. when using the Thonny-IDE.

Work-in progress, Software runs, Readme is unfinished. See instructions in code.
-------------------------------------------




 and the Adafruit Blinka module
 ===============================


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

