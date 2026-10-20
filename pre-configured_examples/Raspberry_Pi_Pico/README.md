# 🍓 Raspberry Pi Pico & Pico 2 Configuration Example

An example configuration for logging sensor data locally using the **Raspberry Pi Pico** or **Pico 2**.

---

## 📋 Prerequisites

* The library is for **CircuitPython 9.x.x**. For higer versions try to run ``circup update --all` (not tested).

---

## 🚀 Quick Start

1. **Copy** all files and directories to the root directory of your microcontroller.
2. **Run the setup script** `switch_RPiPico_to_USB_read_log_mode.py` in the microcontroller's base directory using your PC's CPython interpreter.

**What this script does automatically:**
* Renames the necessary files and folders.
* Restarts your controller.
* Starts logging data directly to the local storage.

### 📊 Accessing Your Data
Once running, you can retrieve your data locally by accessing the on-device files.

---

## 🛠️ Features & Supported Hardware

* **Local Storage Logging:** Saves data directly to the internal storage.
* **I2C Sensors:** Supports all I2C sensors listed in the main repository README.
* **1-Wire Thermosensors:** Supports all 1-Wire sensors listed in the main repository README.

---

## ⚙️ Configuration

1. **Offline Operation:** The following lines are already set in `user_settings.py` since the standard Pico and Pico 2 do not feature wireless connectivity:
   ```python
   USE_HTTP_server = False
   SET_RTC_from_NTP = False
   ```

---

## 🔍 Troubleshooting

* **Live Debugging:** Connect your Pico to **Thonny IDE** and run `code.py`. This allows you to monitor sensor discovery status and the initialization of the data logger.
* **On-Device Storage:** Raw data is stored locally on the microcontroller in the `/logger_data` folder.
* **USB Data Access:** To safely read data over a USB connection, the controller must start up in **non-writing mode**. Please refer to the main repository README for instructions on toggling this mode.
