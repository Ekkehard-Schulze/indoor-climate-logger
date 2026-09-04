Indoor climate logger for CircuitPython/CPython
=====================

Features
--------

- **supported platforms**

  - **CircuitPython:** Supported on microcontrollers (actively tested on **Raspberry Pi Pico**, **Pico W**, and **Pico 2 W**).
  - **Linux:** Supported on Linux PCs and **Raspberry Pi single-board computers** using **CPython**.
  - **Windows:** Supported on PCs using **CPython**.

- **data logging**

  - writes data to a TSV file with ISO 8601 timestamps. Fully compatible with Excel, Google Sheets, and Python (pandas).


- **flexible access on microcontrollers**

  - wirelessly retrieve your data via Wi-Fi when using the **Raspberry&nbsp;Pi&nbsp;Pico&nbsp;2&nbsp;W**, or use it completely offline.


- **cross-Platform & stable** 
  - proven stable through years of real-world deployment on the Pico 2 W using CircuitPython, as well as on Raspberry Pi 3B using CPython and the Adafruit Blinka library.

- **records**

  - precision temperature using up to four I2C sensors
  - general purpose 1-Wire temperature sensors
  - humidity
  - atmospheric pressure
  - carbon dioxide concentration
  - illuminances
radiation surface temperature
  
  
- **supported sensors, all with auto-discovery**

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

- **supported time sources**

  - NTP time for WiFi enabled microcontrollers
  - DS3231 precision RTC for offline applications
  - System time for PC or Raspberry Pi


- **supported I2C to USB interfaces for CPython**

  - Raspberry Pi Pico with U2IF firmware (https://github.com/adafruit/u2if)
  - FT232H
  - MCP2221

### Configuration

You can configure your user settings in one of two ways:

1. **Directly in the main script:** Edit the settings at the top of `indoor-climate-logger.py`.
2. **Using a separate configuration file (Recommended):** Copy `user_settings.template.py` and rename it to `user_settings.py`, then apply your changes there.

> ⚠️ **Note:** If `user_settings.py` exists, it will completely override any settings defined in the header of `indoor-climate-logger.py`.


For microcontrollers running CircuitPython
------------------------------------------

**you need**

- CircuitPython, this code was developed using version 9.2.8 on RaspberrPi Pico2W and Pico2W
- the _/lib_ folder
- to copy these hardware drivers from the Adafruit library bundle (https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) to the _/lib_ folder: 
  - adafruit_register
  - adafruit_tmp117
  - adafruit_adt7410
  - adafruit_bme280
  - adafruit_bme680
  - adafruit_mlx90614
  - adafruit_tsl2561
  - adafruit_onewire
  - adafruit_ds3231
  - adafruit_ntp.
- the main script _indoor-climate-logger.py_ renamed to _code.py_.
- _boot.py_ to mount the filesystem in write mode
- if you want to activate WiFi, edit settings.template.toml with your credentials
  and rename it to settings.toml
  
  **you may like to use**
  - the script _switch_RPiPico_to_USB_read_log_mode.py_, which runs on CPython, renames 
    _boot.py_ to boot.bak on the microcontroller. After a subsequent reset
	of the microcontroller, the logged data are accessible via USB. 
	Use this, if WiFi is not available for data transfer.

 
  - the script _switch_RPiPico_to_write_log_mode.py_, which runs on CPython, renames _boot.bak_ to _boot.py_. 
    For the convenience of the developer, this script also copies _indoor-climate-logger.py_ to _code.py_. 
	After a subsequent reset of the microcontroller, the files system 
	is mounted read/write for the controller and the controller starts logging data. It is not possible
	to read the growing log file via USB.
	
    It is convenient to store the latter two CPython scripts on the microcontroller in order to have them
    accessible when needed. They can be accessed and executed from the PC/Linux-Raspberry Pi even when the
	controller is logging data in write mode. These scripts have been tested so far only under MS-Windows.

For MS-Windows PCs, Linux PCs or Raspberry Pis running CPython
-------------------------------------------------------------

**you need**

 - to install the required **Adafruit Blinka** packages using _pip install -r CPython-requirements.txt_,
  except you only want to use 1-Wire on a Raspberry Pi, which only depends on the kernel driver.

- on a PC you need one of the supported I2C to USB interfaces and you need to use the -u ... option to select the device. 1-Wire is not supported.

- to start the logging script on the command line (e. g. try _indoor-climate-logger.py -h_) and specify either an
  USB-I2C-interface device (Raspberry Pi Pico with U2IF, FT232H, or MCP2221) or choose the Raspberry Pi 
  option. The Raspberry Pi supports 1-Wire for sensor communication alongside I2C using its onboard hardware, and
  UART serial communication using an FT232R USB to serial converter for MH-Z19.

- on Linux systems you can use the _indoor-climate-logger.py -q_ option to append a single data frame
 to the log file when called using a cron-job.


Notes
-------

1. The logger reports time in a fixed time zone defined by 'UTC_offset_hours' when using NTP or CPython time. 
With the DS3231 I2C clock, the logged time is based on the clock's 'set' time with no offset added. 

8. NTP time is supported only for Wifi enabled microcontrollers.

7. On Raspberry Pi I2C is supported via the Adafruit Blinka library. Activate the I2C bus via raspi-config.

3. To use 1-Wire sensors on a Raspberry Pi, activate the 1-Wire bus 
via raspi-config. If you only need 1-Wire based
temperature data logging, you can alternatively use a simpler script provided in  https://github.com/Ekkehard-Schulze/1wire-temperature-logger-RPi instead.


4. On Linux systems _indoor-climate-logger.py_ uses the Linux kernel driver for 1-Wire temperature sensor readings. 
The Linux kernel auto-discovers 1-Wire temperature sensors on startup.
 The kernel supports 1-Wire sensor types DS18S20, DS1822, DS18B20,  DS28EA00,
MAX31850, and DS1825. The latter two read type K thermocouples,
whereas the others are semiconductor thermometers.
The 1-Wire bus can power sensors using 'external power'
(three wires) or 'parasite power' (two wires).
This script was only tested using external power.
   

6. On MS-Windows PCs ADT7420 fails due to a driver bug.

4. The script _plotly_time_series.py_ generates statistics and provides interactive data exploration using Plotly.  Try it using the demo data set _20260222_201501_MHZ_19_CO2_log.tsv_.



	

12. Why is it indoors? Because it is not low power. Consequently, place the sensors at 
least 15 cm away from the controller, to avoid excessive influence of the dissipated thermal 
energy. You still may like to sneak a sensor cable to outdors in addition.

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


11. The default settings were run on multiple Raspberry Pi Pico 2 W using CircuitPython version 9.2.8 
for more than 6 month and are therefore tested for stable continuous operation. A variant of the default settings
using the DS3231 precision clock instead of NTP time was also tested for more than 6 month.



1. The setting "LOG_EXCEPTIONS_to_file = True" sends the exception messages to a log file, to preserve them. This file is accessible 
via http, if the server is set active. However, due to limitations in CicuitPython, these logs
do not contain the normal backtrace information with line numbers. Moreover, this setting
prevents error output to the Repl. This mode is the normal stand alone operation of the logger.


1. For console debugging and developement set "LOG_EXCEPTIONS_to_file = False",
and "WRITE_LOG_data_to_file = False" and have boot.py renamed to boot.bak. This allows
to see standard backtraces and to have USB-write access to the controller.
  



Raspberry Pi Pico, Pico 2, Pico W, Pico 2 W pins and pullup resistors
----------------------------------------------------------------
 6: SDA (GP4)  2.2 kΩ to 3V3
 
 7: SCL (GP5)  2.2 kΩ to 3V3
 
21: RX  (GP17)

22: TX  (GP16)

34: 1-Wire (GP28) 1 kΩ to 3V3


Raspberry Pi Linux SBC pins and pullup resistors
----------------------------------------------------------------
 3: SDA (GPIO 2)  2.2 kΩ to 3V3
 
 5: SCL (GPIO 3)  2.2 kΩ to 3V3
 
 7: 1-Wire (GPIO 4) 4.7 kΩ to 3V3 (do not use parasite power)

 use USB to serial interface FT232R to connect MH-Z19.

Example hardware
------------------------------------------------
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/images/Raspberry_Pi_Pico_2_W_logger.jpg)
                                                                                          
Raspberry Pi Pico 2 W with DS3231 clock module ZS-042 and sensors MH-Z19 (CO2), ADT7420 (indoor precision temperature), BME280 (atmospheric pressure and humidity), and DS18B20 (outdoor temperature). A prototyping PCB, which provides pullup resistors and bus connectors, is plugged to the Raspberry Pi Pico 2 W.


Screenshots from _plotly_time_series.py_
------------------------------------------------

**Time course** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/time_course_screenshot.webp)

**Descriptive statistics** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/descriptive_statistics_screenshot.webp)

Plotly is an interactive data exploration tool.

