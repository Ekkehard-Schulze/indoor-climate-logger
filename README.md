Indoor climate data logger 
=====================

**for**

- microcontrollers running CircuitPython

- MS-Windows PCs using CPython

- Linux/RaspberryPi using CPython

**can record**

- precision temperature of multiple sensors and sensor types
- humidity
- atmospheric pressure
- carbon dioxide concentration using non-dispersive spectrometry
- illuminance
- contactless surface temperature of an object

**uses one out of three time sources**

- NTP time for WiFi enabled microcontrollers
- DS3231 precision RTC for non-Network applications
- System time as a fallback or on CPython PCs

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
- _indoor-climate-logger.py_ renamed to _code.py_, header edited for your desired user settings
- _boot.py_
- if you want to activate WiFi, edit settings_template.toml with your credentials
  and rename it to settings.toml
- edit the user setting either in the head of _indoor-climate-logger.py_, or, alternatively, in
  _user_settings.template.py_, which then must be saved as user_settings.py. If _user_settings.py_
  is present, it will override the setting in the head of _indoor-climate-logger.py_.
  
  **you may like to use**
  - The script _switch_RPiPico_to_USB_read_log_mode.py_ runs in CPython and renames _boot.py_ to boot.bak on the microcontroller, when 
	plugged to a USB port, even when the filesystem is mounted read-only. After a reset or
	re-plug of the microcontroller, the files system is mounted read only for the controller,
	and now log data can be copied to the PC. This is required, WiFi is not available or not
	activated. For convenience, this script may be located on the controller, however it also functions when
	located on the PC.
 
  - The script _switch_RPiPico_to_write_log_mode.py_ runs in CPython and renames _boot.bak_ to _boot.py_. For the
    convenience of the developer, it also copies _indoor-climate-logger.py_ to _code.py_ and offers to
	delete _indoor-climate-logger.py_. After a reset or e-plug of the microcontroller, the the files system 
	is mounted read write for the controller and the controller starts logging data. It is not possible
	to read the growing log file via USB, however in verbose mode the data are also printed to the
	repl, e. g. when using the Thonny-IDE. For convenience, this script may be located on the controller, however it also functions when
	located on the PC.


For MS-Windows PCs, Linux PCs or RaspberryPis 
----------------------------------------------

**you need**

 - to install the required **Adafruit Blinka** packages using _pip install -r CPython-requirements.txt_. The 
  latter is located in the utilit_scripts folder. Except you only want to use 1Wire on the RaspberryPi,
  in this case no software installation is required.

- edit the user setting either in the head of _indoor-climate-logger.py_, or, alternatively, in
  user_settings.template.py, which then must be saved as user_settings.py. If _user_settings.py_
  is present, it will override the setting in the head of _indoor-climate-logger.py_.

- use the command line start (enter _indoor-climate-logger.py -h_) and specify either an
  USB-I2C-interface device (RapberryPi Pico with U2IF, FT232H, or MCP2221) or choose the RaspberryPi option. The Raspberry Pi supports 1Wire for 
  sensor communication alongside I2C. 

Supported sensors
-------------------------------------------

Sensors implemented with auto detect (auto-detect requires activation of the specific bus in this code)

- i2c
  - TMP117   temperature 0.1°C precision
  - ADT7420  temperature 0.2°C precision
  - mlx90614 temperature IR  0.5°C precision
  - bme280   barometric pressure, humidity 3%, temperature ±1°C (0.5°C at 25°C) 
  - bme680   barometric pressure, humidity 3%, temperature ±1°C 
  - tsl2561  illuminance

- 1Wire
  - DS18B20  ±0.5°C Accuracy from -10°C to +85°C
  - DS18S20  ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  - DS1820   ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  - MAX31850 ±2°C for temperatures  -200°C to +700°C

- serial rx tx
  - MH-Z19   carbon dioxide concentration



 technical details
---------------------


On Linux systems this Python script uses the Linux kernel driver for temperature readings. 

The 1-Wire bus enables multiple temperature sensors on a single long cable.

The Linux kernel auto-discovers 1-Wire temperature sensors on startup.

You can connect different types of sensors to the same bus. The kernel 

supports 1-Wire sensor types DS18S20, DS1822, DS18B20,  DS28EA00,

MAX31850, and DS1825. The latter two read type K thermocouples,

whereas the others are semiconductor sensors.





Notes
-------

1.) MS-Z19 carbon dioxide measurement is only supported on microcontrollers running Circuit Python

2.) On MS-Windows PCs only I2C-Sernsors are supported. ADT720 fails due to a driver bug.

3.) On a Raspberry Pi kernel 1Wire and Blinka I2C are supported.

4.) The script either logs temperature measurements with Python's timer or RTC,
    or with a DS3231 I2C precision clock.    On WiFi enabled microcontroller, NTP
	is also supported

5.) The script writes a tab separated value formatted text file with 

ISO 8601 date and time. This format is compatible with python's pandas 

and plotly packages as well as with spreadsheet processing. 

6.) The script _plotly_time_series.py_ server for generating statistics and interacvtive data 
    exploration using plotly.  Try it using the demo data set _20260222_201501_MHZ_19_CO2_log.tsv_.




Never forget
---------------------
The script _user_settings.py_ overrides the settings in the head of _indoor-climate-logger.py_. This is convenient,
if you want to configure multiple loggers and use and maintain the same 
_indoor-climate-logger.py/code.py_ for all of them. With one logger, remove user_settings.py and 
edit settings in _indoor-climate-logger.py/code.py_ instead.


Why is it indoors?
---------------------
Because it is not low power. Consequently, place the sensors at least 15 cm away from the
controller, to avoid excessive influence of the dissipated thermal power.
