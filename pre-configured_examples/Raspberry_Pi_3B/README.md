# 🐧 Raspberry Pi 3B Configuration Example

An example configuration for logging sensor data locally using a **Raspberry Pi 3B** running Linux.

---

## 📋 Prerequisites

* **Python 3 (CPython)** must be installed on your Raspberry Pi.
* **Hardware Interfaces:** Ensure that **I2C** and **1-Wire** are enabled on your Raspberry Pi 3B. You can activate them via the terminal configuration tool:

```bash
sudo raspi-config
```
*Navigate to `Interface Options` to enable both **I2C** and **1-Wire**, then reboot your Pi.*

* Ensure you have the necessary **dependencies** installed before running the application:

```bash
pip install -r requirements_for_CPython.txt
```

---

## 🚀 Quick Start

1. **Copy** `indoor-climate-logger.py` and optionally also `user_settings.py` to your working directory.
2. **Run the main application script** `indoor-climate-logger.py` directly from your terminal:

```bash
python3 ./indoor-climate-logger.py
```

> 💡 **Tip:** You can run `python3 ./indoor-climate-logger.py -h` to view all available command-line options and configurations.

**What the system does automatically:**
* Initializes connected sensors.
* Starts logging data directly to local storage.

### ⏱️ Automated & Scheduled Logging (Crontab)
For periodic logging, you can run the script via a cron job using the `-q` option.
* **Single Frame Mode:** The `-q` option forces the script to log a **single data frame** and then exit immediately.
* **Example Crontab Entry:** To log data automatically every 15 minutes, add the following line to your `crontab -e`:

```text
*/15 * * * * cd /path/to/your/folder && python indoor-climate-logger.py -q >/dev/null 2>>/dev/null
```

### 📊 Accessing Your Data
Once running, you can retrieve your data locally by accessing the generated log files within your application folder.

---

## 🛠️ Features & Supported Hardware

* **Local Storage Logging:** Saves data directly to the internal storage.
* **I2C Sensors:** Supports all I2C sensors listed in the main repository README.
* **1-Wire Thermosensors:** Supports all 1-Wire sensors listed in the main repository README.

---

## 🔍 Troubleshooting

* **Live Debugging:** Run the main script directly from your terminal without the `-q` option to monitor sensor discovery status and the initialization of the data logger via standard output.
* **On-Device Storage:** Raw data is stored locally in the `/logger_data` folder within your application directory.

