Indoor climate logger for CircuitPython/CPython
=====================

Features
--------

- **supported platforms**

  - **CircuitPython:** Supported on microcontrollers (actively tested on **Raspberry Pi Pico**, **Pico W**, and **Pico 2 W**).
  - **Linux:** Supported on **Linux PCs** and **Raspberry Pi single-board computers** using **CPython**.
  - **Windows:** Supported on **PCs** using **CPython**.

- **data logging**

  - writes data to a TSV file with ISO 8601 timestamps. Fully compatible with Excel, Google Sheets, and Python (pandas).


- **flexible access on microcontrollers**

  - wirelessly retrieve your data via Wi-Fi when using the **Raspberry&nbsp;Pi&nbsp;Pico&nbsp;2&nbsp;W**, or use it completely offline.


- **cross-Platform & stable** 
  - proven stable through years of real-world deployment on the Pico 2 W using CircuitPython, as well as on Raspberry Pi 3B using CPython and the Adafruit Blinka library.

- **records**

  - accurate temperature using up to four I2C sensors
  - general purpose 1-Wire temperature sensors
  - humidity
  - atmospheric pressure
  - carbon dioxide concentration
  - illuminances
radiation surface temperature
  
  
- **supported sensors, all with auto-discovery**

  - i2c
    - TMP117   temperature ±0.1 °C accuracy
    - ADT7420  temperature ±0.2 °C accuracy
    - mlx90614 temperature IR ±0.5 °C accuracy
    - bme280   barometric pressure, humidity 3%, temperature ±1 °C accuracy
    - bme680   barometric pressure, humidity 3%, temperature ±1 °C accuracy
    - tsl2561  illuminance

  - 1-Wire
    - DS18B20  ±0.5 °C accuracy from -10 °C to +85 °C
    - DS18S20  ±0.5 °C accuracy from -10 °C to +85 °C (obsolete)
    - DS1820   ±0.5 °C accuracy from -10 °C to +85 °C (obsolete)
    - MAX31850 ±2 °C for temperatures  -30 °C to +600 °C (using type K thermocouples)

  - serial rx tx
    - MH-Z19   carbon dioxide concentration  

- **supported time sources**

  - NTP time for WiFi enabled microcontrollers
  - DS3231 extremely accurate RTC for offline applications
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

## Requirements for CircuitPython Microcontrollers

This project was developed and tested using **CircuitPython 9.2.8** on the **Raspberry Pi Pico 2 W**.

To get started, you will need to copy the following files and folders to your microcontroller:

* The `/lib` folder from this repository.
* The following hardware drivers from the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) (placed inside the `/lib` folder):
  * `adafruit_register`
  * `adafruit_tmp117`
  * `adafruit_adt7410`
  * `adafruit_bme280`
  * `adafruit_bme680`
  * `adafruit_mlx90614`
  * `adafruit_tsl2561`
  * `adafruit_onewire`
  * `adafruit_ds3231`
  * `adafruit_ntp`
* The main script `indoor-climate-logger.py`, renamed to `code.py`.
* The `boot.py` file (required to mount the filesystem in write mode).
* **Optional WiFi Setup:** If you want to enable WiFi, add your credentials to `settings.template.toml` and rename it to `settings.toml`.

## Optional Utility Scripts

You can also use the following helper scripts, which run on your host PC via **CPython**:

* **`switch_RPiPico_to_USB_read_log_mode.py`**
  Renames `boot.py` to `boot.bak` on the microcontroller. After resetting the board, the logged data will be accessible via USB. Use this method if WiFi is unavailable for data retrieval.
* **`switch_RPiPico_to_write_log_mode.py`**
  Renames `boot.bak` back to `boot.py`. For development convenience, this script also automatically copies `indoor-climate-logger.py` to `code.py`. After a subsequent reset, the filesystem is mounted in read/write mode for the microcontroller, and logging begins. Note that you cannot read the active log file via USB while in this mode.

*Tip: It is convenient to store these two CPython scripts directly on the microcontroller so they are always available. They can be executed from a PC (Windows, Linux, or Raspberry Pi) even while the controller is actively logging data in write mode. Note that these scripts have currently only been tested on MS Windows.*

	
## Requirements for Host PCs (Windows, Linux, Raspberry Pi) running CPython

### 1. Prerequisites

First, install the required Adafruit Blinka packages by running:
```bash
pip install -r CPython-requirements.txt
```

### 2. Supported Hardware Compatibility

| Platform | I2C Support | 1-Wire Support | UART (FT232R for MH-Z19) |
| :--- | :--- | :--- | :--- |
| **MS-Windows PC** | Supported via I2C-to-USB interface | Not supported | Not yet supported (can be manually added by changing the serial port name in the code) |
| **Linux PC** | Supported via I2C-to-USB interface (On-board I2C not supported) | Supported only if native hardware & Linux kernel support it | Supported |
| **Raspberry Pi** | Supported via Adafruit-Blinka | Supported via Linux kernel driver | Supported |

### 3. Usage

To run the logging script, use the command line. You can check the available options by running:
```bash
python indoor-climate-logger.py -h
```

When starting the script, you must specify your hardware setup using the `-u` option:
* Select an external USB-I2C interface device (e.g., **Raspberry Pi Pico with U2IF**, **FT232H**, or **MCP2221**).
* Or select the native **Raspberry Pi** hardware directly.

#### Automation on Linux (Cron jobs)
On Linux systems, you can use the `-q` (quiet/quick) option to append a single data frame to the log file:
```bash
python indoor-climate-logger.py -q
```
*Tip: Calling the script with this option via a **cron job** is the preferred and most reliable way to run it on Linux.*
	


## Notes

* **Time Management:** The logger reports time in a fixed time zone defined by `UTC_offset_hours` when using NTP or CPython time. When using the DS3231 I2C clock, the logged time is based strictly on the clock's set time (no offset is added).
* **Network Restrictions:** NTP time is only supported on Wi-Fi-enabled microcontrollers.
* **Raspberry Pi Configuration:** Activate the I2C and 1-Wire buses via `raspi-config`. The 1-Wire bus supports both external power (3-wire) and parasite power (2-wire), though this script has only been tested with external power. 
  * *Alternative:* If you only need simple 1-Wire temperature logging, consider using the more lightweight script available at [1wire-temperature-logger-RPi](https://github.com/Ekkehard-Schulze/1wire-temperature-logger-RPi). That script also extends the Type K thermocouple range (via MAX31850) from -200 °C to +1200 °C using ITS-90 standard corrections.
* **Windows Compatibility:** The ADT7420 sensor fails on MS-Windows PCs due to an underlying driver bug.
* **Data Visualization:** The `plotly_time_series.py` script generates statistics and offers interactive data exploration. You can test it out using the provided demo dataset: `20260222_201501_MHZ_19_CO2_log.tsv`.
* **Thermal Dissipation Warning:** This is designed as an indoor logger because it is **not** a low-power application. To prevent the controller's dissipated heat from altering your readings, position all sensors at least 15 cm away from the board. You can, however, route an extra sensor cable outdoors.

---

## Notes for CircuitPython

### Storage & Data Retrieval
* **Rolling Storage:** Due to limited flash memory on microcontrollers, data is stored using a rolling system to enable infinite, continuous operation. To create long-term logs, you should periodically poll and merge the data onto a secondary system using the helper scripts found in `./utility_scripts/data_retrieval_merge_and_cleaning`.
* **Filesystem Lock (Standalone Mode):** During startup, `boot.py` mounts the filesystem as read/write for the microcontroller. This locks out the PC, meaning you cannot write to the board or read the growing log files over USB. This is the default standalone logging mode.
* **Unlocking USB Storage:** To safely harvest data from a logger without Wi-Fi, you must disable the local write mode:
  1. Run the following REPL command: `import os; os.rename("/boot.py", "/boot.bak")`
  2. Reset the microcontroller.
  The filesystem will now be fully accessible from your PC via USB, but logging is paused. Alternatively, you can run the host-side script `switch_RPiPico_to_USB_read_log_mode.py` while the board is connected via USB.

### Library & Hardware Quirks
* **HTTP Server:** The `/lib/adafruit_httpserver` module is sourced from CircuitPython 8.2.6. The version included in CircuitPython 9.2.8 is intentionally skipped due to breaking, incompatible changes.
* **1-Wire / Parasite Power Warning:** The `/lib/schulze_one_wire_temperature.py` module is a customized fork of `adafruit_ds18x20` (from version 8.2.6), modified to support more sensor types and improve parasite power performance. 
  * *Hardware Note:* Testing revealed that an 820 Ω pull-up resistor is required when using multiple DS18X20 sensors (and 450 Ω for the MAX31850), instead of the standard 4.7 kΩ resistor. This strongly indicates that the 1-Wire protocol implementation in MicroPython/CircuitPython, as well as the Linux kernel, handles parasite power poorly. For larger setups, **do not use parasite power**—always opt for a standard 3-wire connection.

### Stability & Debugging
* **Long-Term Testing:** The default settings have been stress-tested on multiple Raspberry Pi Pico 2 W boards running CircuitPython 9.2.8 for over 6 months of continuous, stable operation. A setup utilizing the precise DS3231 hardware clock (instead of NTP) was verified over an identical 6-month period.
* **Production Logging:** Setting `LOG_EXCEPTIONS_to_file = True` saves exception messages directly to a file (accessible via HTTP if the web server is running). Note that CircuitPython limitations prevent these logs from containing standard backtraces or line numbers. This setting also mutes error outputs to the REPL.
* **Development Mode:** For live console debugging, use these settings:
  ```python
  LOG_EXCEPTIONS_to_file = False
  WRITE_LOG_data_to_file = False
  ```
  Then rename `boot.py` to `boot.bak`. This restores full USB write access to the PC and enables standard error backtraces in your terminal.



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
<br/>
<br/>

Example hardware
------------------------------------------------
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/images/Raspberry_Pi_Pico_2_W_logger.jpg)
                                                                                          
A Raspberry Pi Pico 2 W equipped with a DS3231 (ZS-042) real-time clock module and a suite of sensors: an MH-Z19 for CO2, an ADT7420 for accurate indoor temperature, a BME280 for atmospheric pressure and humidity, and a DS18B20 for outdoor temperature. The setup is connected via a custom prototyping PCB that plugs into the Pico 2 W, providing necessary pull-up resistors and bus connectors. LED, EEPROM and the battery charging circuit were removed from the ZS-042 clock board for power optimization. 
<br>
<br>
<br>

![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/images/Raspberry_Pi_3B.jpg)
                                                                                          
A Raspberry Pi 3B equipped with an MH-Z19 CO2 sensor (connected via an FT232R serial UART interface), an ADT7420 for accurate indoor temperature, and a BME280 for atmospheric pressure and humidity. The sensors are integrated using an I2C bus PCB that provides pull-up resistors and connectors.
<br>
<br>
<br>

![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/images/Raspi_with_1-Wire_bus.jpg)
<p>Experimental setup for monitoring mercury arc lamp usage over a two-year period. The system consists of an 8-meter 1-Wire bus cable with six DS18B20 temperature sensors connected to a Raspberry Pi 3B+. Neodymium magnets secure the 
sensors to the equipment</p>
<br/>
<br/>
<br/>

![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/images/Raspi_with_typeK_thermocouples.jpg)
<p>Four Type K thermocouples, connected via MAX31850 amplifiers to a Raspberry Pi 3B+, enable temperature measurements ranging from -30 °C to 600 °C.</p>
<br/>
<br/>
<br/>

Screenshots from _plots_and_statistics_of_time_series.py_
-----------------------------------------

**Time course** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/time_course_screenshot.webp)

**Descriptive statistics** 
![Sensor chan](https://github.com/Ekkehard-Schulze/indoor-climate-logger/blob/main/utility_scripts/plotting_and_statistics_with_demo_data/screenshots/descriptive_statistics_screenshot.webp)
Screenshot of interactive data visualization using the script plots_and_statistics_of_time_series.py.

