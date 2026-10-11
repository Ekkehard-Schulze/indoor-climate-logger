# 🍓 Raspberry Pi Configuration Example

An example configuration for logging sensor data locally using a standard **Raspberry Pi** running Linux.

---

## 📋 Prerequisites

* **Python 3 (CPython)** must be installed on your Raspberry Pi.
* Ensure you have the necessary **dependencies** installed before running the application:

```bash
pip install -r requirements_for_CPython.txt
```

---

## 🚀 Quick Start

1. **Copy** all files and directories to any directory of your choice on your Raspberry Pi.
2. **Run the main application script** (e.g., `code.py` or your main script execution command) directly from your terminal.

**What the system does automatically:**
* Initializes connected sensors.
* Starts logging data directly to local storage.

### 📊 Accessing Your Data
Once running, you can retrieve your data locally by accessing the generated log files within your application folder.

---

## 🛠️ Features & Supported Hardware

* **Local Storage Logging:** Saves data directly to the internal storage.
* **I2C Sensors:** Supports all I2C sensors listed in the main repository README.
* **1-Wire Thermosensors:** Supports all 1-Wire sensors listed in the main repository README.

---

## ⚙️ Configuration

1. **Offline Operation:** Ensure the following lines are set in `user_settings.py` since network features are disabled:
   ```python
   USE_HTTP_server = False
   SET_RTC_from_NTP = False
   ```

---

## 🔍 Troubleshooting

* **Live Debugging:** Run the main script directly from your terminal to monitor sensor discovery status and the initialization of the data logger via standard output.
* **On-Device Storage:** Raw data is stored locally in the `/logger_data` folder within your application directory.
