# 🍓 Raspberry Pi Pico W Configuration Example

An example configuration for logging and serving sensor data over WLAN using the Raspberry Pi Pico W.

---

## 📋 Prerequisites

* **CircuitPython 9.8** must be pre-installed on your microcontroller before setting up this configuration.

---

## 🚀 Quick Start

1. **Copy** the configuration files to the root directory of your microcontroller.
2. **Run the setup script** `switch_RPiPico_to_USB_read_log_mode.py` on your PC using a standard CPython interpreter.

**What this script does automatically:**
* Renames the necessary files and folders.
* Restarts your controller.
* Connects to your WLAN network.
* Starts logging data and serving it directly to the web.

### 📊 Accessing Your Data
Once running, you can retrieve your data locally at the following URLs:
* 📋 **Data Log:** http://192.168.178
* ⚠️ **Exception Log:** http://192.168.178 *(Note: Verify if the filename typo "expeptions" is required by your script)*

---

## 🛠️ Features & Supported Hardware

* **WLAN Data Serving:** Hosts a local web server to expose log files.
* **I2C Thermosensors:** Full support for **TMP117** and **ADT7420**.
* **1-Wire Thermosensors:** Supported out of the box.

---

## ⚙️ Configuration

1. **Network Setup:** Enter your WLAN credentials in the `settings.toml` file.
2. **Offline Mode (Optional):** To run this without WLAN on a standard **Raspberry Pi Pico** or **Pico 2**, change the following lines in `user_settings.py`:
   ```python
   USE_HTTP_server = False
   SET_RTC_from_NTP = False
   ```

---

## 🔍 Troubleshooting

* **Live Debugging:** Connect your Pico to **Thonny IDE** and run `code.py`. This allows you to monitor the WLAN connection process, sensor discovery status, and the initialization of the data logger.
* **On-Device Storage:** Raw data is stored locally on the microcontroller in the `/logger_data` folder.
* **USB Data Access:** To safely read data over a USB connection, the controller must start up in **non-writing mode**. Please refer to the main repository README for instructions on toggling this mode.
