# 🍓 Raspberry Pi Pico W Configuration Example

An example configuration for logging and serving sensor data over WLAN using the Raspberry Pi Pico W.

---

## 📋 Prerequisites

* The library is for **CircuitPython 9.x.x**. For higer versions try to run ``circup update --all` (not tested).

---

## 🚀 Quick Start

1. **Copy files:** Copy all files and directories to the root directory of your microcontroller.
2. **Set up network:** 
   * Enter your Wi-Fi credentials into the `settings.toml` file.
   * Enter your IP configuration into the `user_settings.py` file as follows:

   ```python
   IPV4 = "192.168.178.143"
   NETMASK = "255.255.255.0"
   GATEWAY = "192.168.178.1"
   ```

> 💡 **Note:** Replace `192.168.178.xxx` with your microcontroller's actual IP address configuration if yours is different.


2. **Run the setup script** `switch_RPiPico_to_USB_read_log_mode.py` in the microcontrollers base directory using your PC's CPython interpreter.

**What this script does automatically:**
* Renames the necessary files and folders.
* Restarts your controller, 
which then:
* Connects to your WLAN network.
* Starts logging data and serving it directly to the web.

### 📊 Accessing Your Data

Once running, you can retrieve your data locally at the URLs below. 

> 💡 **Note:** Replace `192.168.178.143` with your microcontroller's actual IP address configuration if yours is different.

* 📋 **Data Log:** http://192.168.178.143//logger-data.tsv
* ⚠️ **Exception Log:** http://192.168.178.143//exceptions_log.txt

---

## 🛠️ Features & Supported Hardware

* **WLAN Data Serving:** Hosts a local web server to expose log files.
* **I2C Sensors:** Supports all I2C sensors listed in main repository README
* **1-Wire Thermosensors:** Supports all 1-Wire sensors listed in main repository README

---

## 🔍 Troubleshooting

* **Live Debugging:** Connect your Pico to **Thonny IDE** and run `code.py`. This allows you to monitor the WLAN connection process, sensor discovery status, and the initialization of the data logger.
* **On-Device Storage:** Raw data is stored locally on the microcontroller in the `/logger_data` folder.
* **USB Data Access:** To safely read data over a USB connection, the controller must start up in **non-writing mode**. Please refer to the main repository README for instructions on toggling this mode.
