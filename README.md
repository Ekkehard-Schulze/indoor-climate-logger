Indoor climate logger for CircuitPython/CPython
=====================

**Writes a tabulator separated text file with data, date and time**

Features
--------

- **optional online clima monitoring via WiFi**

  - available for RaspberryPi PicoW and Pico2W

- **can record**

  - precision temperature using up to four I2C sensors
  - general purpose temperature using more than eight 1-Wire sensors
  - humidity
  - atmospheric pressure
  - carbon dioxide concentration
  - illuminance
  - radiation surface temperature

- **implemented for**

  - microcontrollers running CircuitPython

  - MS-Windows PCs using CPython

  - Linux PCs/RaspberryPis using CPython

- **uses one out of three time sources**

  - NTP time for WiFi enabled microcontrollers
  - DS3231 precision RTC for offline applications
  - System time for PC or Raspberry Pi


- **allows three types of I2C to USB interfaces for PCs**

  - RaspberryPi Pico with U2IF firmware (https://github.com/adafruit/u2if)
  - FT232H
  - MCP2221


For microcontrollers running CircuitPython
------------------------------------------

**you need**

- CircuitPython, this code was developed using version 9.2.8 on RaspberrPi Pico2W and Pico2W
- the _/lib_ folder
- these hardware drivers from the Adafruit library bundle for your CircuitPython version:
  https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases: adafruit_register, adafruit_tmp117, adafruit_adt7410, 
  adafruit_bme280, adafruit_bme680, 
  adafruit_mlx90614, adafruit_tsl2561,
  adafruit_onewire, adafruit_ds3231, adafruit_ntp.\
  Copy these to the _/lib_ folder. You may omit the drivers for sensors you do not use.
- to edit the user setting either in the head of _indoor-climate-logger.py_, or, alternatively, in the optional script
  _user_settings.template.py_, which then must be saved as user_settings.py. If _user_settings.py_
  is present, it will override the settings in the head of _indoor-climate-logger.py_.
- the main script _indoor-climate-logger.py_ renamed to _code.py_.
- _boot.py_ to mount the filesystem in write mode
- if you want to activate WiFi, edit settings.template.toml with your credentials
  and rename it to settings.toml
  
  **you may like to use**
  - the script _switch_RPiPico_to_USB_read_log_mode.py_, which runs on the PC and renames 
    _boot.py_ to boot.bak on the microcontroller. After a subsequent reset
	of the microcontroller, the logged data are accessibel for the PC. 
	This is required, if WiFi is not available for data transfer.

 
  - the script _switch_RPiPico_to_write_log_mode.py_, which runs on the PC and renames _boot.bak_ to _boot.py_. 
    For the
    convenience of the developer, this script also copies _indoor-climate-logger.py_ to _code.py_. 
	After a subsequent reset of the microcontroller, the files system 
	is mounted read/write for the controller and the controller starts logging data. It is not possible
	to read the growing log file via USB.

For MS-Windows PCs, Linux PCs or RaspberryPis running CPython
-------------------------------------------------------------

**you need**

 - to install the required **Adafruit Blinka** packages using _pip install -r CPython-requirements.txt_.
  Except you only want to use 1-Wire on a RaspberryPi, which only depends on the kernel driver.

- to edit the user setting either in the head of _indoor-climate-logger.py_, or, alternatively, in the optional script
  user_settings.template.py, which then must be saved as user_settings.py. Attention: If _user_settings.py_
  is present, it will override the setting in the head of _indoor-climate-logger.py_.

- to start the logging script on the command line (e. g. _indoor-climate-logger.py -h_) and specify either an
  USB-I2C-interface device (RaspberryPi Pico with U2IF, FT232H, or MCP2221) or choose the RaspberryPi 
  option. The Raspberry Pi supports 1-Wire for sensor communication alongside I2C. 

Supported sensors
-------------------------------------------

Sensors are implemented with auto detect. This, however, requires activation 
of the respective bus in the user settings.

- i2c
  - TMP117   temperature 0.1°C precision
  - ADT7420  temperature 0.2°C precision
  - mlx90614 temperature IR  0.5°C precision
  - bme280   barometric pressure, humidity 3%, temperature ±1°C
  - bme680   barometric pressure, humidity 3%, temperature ±1°C 
  - tsl2561  illuminance

- 1-Wire
  - DS18B20  ±0.5°C Accuracy from -10°C to +85°C
  - DS18S20  ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  - DS1820   ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  - MAX31850 ±2°C for temperatures  -200°C to +700°C

- serial rx tx
  - MH-Z19   carbon dioxide concentration



1-Wire temperature sensors on RaspberryPi/Linux
-----------------------------------------------------------

On Linux systems _indoor-climate-logger.py_ uses the Linux kernel driver for temperature readings. 
The 1-Wire bus enables multiple temperature sensors on a single long cable.
The Linux kernel auto-discovers 1-Wire temperature sensors on startup.
You can connect different types of sensors to the same bus. The kernel 
supports 1-Wire sensor types DS18S20, DS1822, DS18B20,  DS28EA00,
MAX31850, and DS1825. The latter two read type K thermocouples,
whereas the others are semiconductor thermometers.
The 1-Wire bus can power sensors using 'external power'
(three wires) or 'parasite power' (two wires).
This script was only tested using external power.
To use 1-Wire sensors with a Raspberry Pi, activate the 1-Wire bus 
via raspi-config. The default Raspberry Pi GPIO pin for 
1-Wire communication is GPIO4. You need a 4.7kΩ resistor 
between the data line and 3.3 volt. If you prefer crontab triggered 1-Wire 
sensor data logging, you can use https://github.com/Ekkehard-Schulze/1wire-temperature-logger-RPi, which 
provides a much leaner solution.


Notes
-------

1. _indoor-climate-logger.py_ writes a tab separated value formatted text file with 
ISO 8601 date and time. This format is compatible with python's pandas 
and plotly packages as well as with spreadsheet processing. 

2. The logger reports time in a fixed time zone defined by 'UTC_offset_hours' when using NTP or CPython time. 
With the DS3231 I2C clock, the logged time is based on the clock's 'set' time with no offset added. 

8. NTP time is supported only for Wifi enabled microcontrollers.
   
3. The optional script _user_settings.py_ overrides the settings in the head of _indoor-climate-logger.py_. This is convenient for configuring 
multiple loggers with the same indoor-climate-logger.py script. For a single logger, delete user_settings.py and edit 
the settings in _indoor-climate-logger.py_. 

4. The script _plotly_time_series.py_ generates statistics and provides interactive data exploration using Plotly.  Try it using the demo data set _20260222_201501_MHZ_19_CO2_log.tsv_.


5. MH-Z19 carbon dioxide measurement is only supported on microcontrollers running Circuit Python.

6. On MS-Windows PCs only I2C-sensors are supported. ADT7420 fails due to a driver bug.

7. On Raspberry Pi kernel driven 1-Wire and Blinka I2C are supported.

	

12. Why is it indoors? Because it is not low power. Consequently, place the sensors at 
least 15 cm away from the controller, to avoid excessive influence of the dissipated thermal 
power. You may like to sneak a sensor cable to outdors in addition.

Notes for CircuitPython
---------------------------------------------------------

1. On a microcontroller the limited flash memory is used as rolling storage, to allow for continous infinite operation. 
Generate a long-term log file by periodic data polling and merging on a secondary system. Find the respective scripts 
in _./utility_scripts/data_retrieval_merge_and_cleaning_.

1. boot.py mounts the controller's filesystem to read/write during startup, which prevents
   write access from PC via USB. Moreover, the growing log files can not be read from the PC via USB.
   This mode is the normal stand alone operation of the logger.


1. A Repl command to stop write mode is _import os; os.rename("/boot.py", "/boot.bak")_ followed by a reset.
Now the filesystem is fully accessible from the PC via USB, however the logger can no longer write
to its file system. This mode is used to harvest
the logged data from non WiFi enabled loggers. This setting can also be issued via the USB-serial
 connection using the _switch_RPiPico_to_USB_read_log_mode.py_ script on the PC, when the
controller is attached via USB.

9.	The adafruit_httpserver module in /lib is source code from CircuitPython version 8.2.6. 
The respective module of CircuitPython 9.2.8 is not used, because it contains
incompatible changes.


10.	The module schulze_one_wire_temperature.py in /lib is a forked 
adafruit_ds18x20 source code from CircuitPython version 8.2.6. 
The fork was done to improve performance with 'parasite power' and to allow usage of
additional sensor types. Attention:  in addition to the code modification I needed
a 820 Ohm pullup resistor if I used more than one DS18X20 Sensor and 450 Ohm für MAX31850,
instead of the usual 4k7 used in sensor data sheets. This is an indication that the implementation
of the 1-Wire protocol in Micropython/CircuitPython and as well in the Linux kernel does not handle
1-Wire parasite power in a proper way. Consequently, you can not use parasite power
for larger installations, use standard power via a 3-wire connection instead.


11. The default settings were run on multiple RaspberryPi Pico2Ws using CircuitPython version 9.2.8 
for more than 6 month and are therefore tested for stable continuous operation. A variant of the default settings
using the DS3231 precision clock instead of NTP time was also tested for more than 6 month.



1. The setting "LOG_EXCEPTIONS_to_file = True" sends the exception messages to a log file, to preserve them. This file is accessible 
via http, if the server is set active. However, due to limitations in CicuitPython, these logs
do not contain the normal backtrace information with line numbers. Moreover, this setting
prevents error output to the Repl. This mode is the normal stand alone operation of the logger.


1. For console debugging and developement set "LOG_EXCEPTIONS_to_file = False",
and "WRITE_LOG_data_to_file = False" and have boot.py renamed to boot.bak. This allows
to see standard backtraces and to have USB-write access to the controller.
  



RaspberryPi Pico, Pico2, PicoW, Pico2W pins and pullup resistors
----------------------------------------------------------------
 6: SDA (GP4)  2.2 kΩ to 3V3
 
 7: SCL (GP5)  2.2 kΩ to 3V3
 
21: RX  (GP17)

22: TX  (GP16)

34: 1-Wire (GP28) 1 kΩ to 3V3



Screenshots from _plotly_time_series.py_
------------------------------------------------
note: Plotly is an interactive data exploration tool



**Time course** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/time_course_screenshot.webp)

**Descriptive statistics** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/descriptive_statistics_screenshot.webp)

