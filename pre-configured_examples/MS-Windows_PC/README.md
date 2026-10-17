# 🪟 Indoor Climate Logger Configuration Example

An example configuration for logging sensor data locally on a **Windows PC** using a USB-to-I2C interface hardware module.

---

## 📋 Prerequisites

* **Python 3 (CPython)** must be installed on your Windows system.
* Ensure you have the necessary **dependencies** installed before running the application:

```cmd
pip install -r requirements_for_CPython.txt
```

---

## 🚀 Quick Start

1. **Copy** all files and directories to any folder of your choice on your PC.
2. **Open your command prompt** (cmd) or PowerShell in that directory.
3. **Run the main application script** `indoor-climate-logger.py` and specify your USB-to-I2C bridge hardware using the `-u` or `--USB_IC` flag:

```cmd
python indoor-climate-logger.py --USB_IC 1
```

### 🔌 Available USB-to-I2C Interfaces
When launching the script, select your hardware by passing the corresponding number to the `-u` / `--USB_IC` argument:
* `0`: RPi (Not applicable on Windows)
* `1`: **FT232H** *(Note: If using an FT232R, see driver requirements below)*
* `2`: **MCP2221**
* `3`: **RPi Pico U2IF**

*Example:* Use `python indoor-climate-logger.py -u 2` or `python indoor-climate-logger.py --USB_IC 2` if you are using an MCP2221 breakout board.

> [!IMPORTANT]
> **FTDI / FT232R Driver Note:**  
> If you are using an **FT232R**, the script will fail with the standard Windows default FTDI driver installed. To make it work, you must replace the default driver with the **libusbK** driver using the tool **Zadig**.

### 📊 Accessing Your Data
Once running, you can retrieve your data locally by accessing the generated log files within your application folder.

---

## 🛠️ Features & Supported Hardware

* **Local Storage Logging:** Saves data directly to your local drive.
* **I2C Sensors:** Supports all I2C sensors listed in the main repository README via a supported USB interface.
⚠️ 
    **Note:** The ADT7420 sensor fails on MS-Windows PCs due to an underlying driver bug.

---

## 🔍 Troubleshooting

* **Live Debugging:** Run the script from the command line to monitor sensor discovery status and the initialization of the data logger via standard console output.
* **On-Device Storage:** Raw data is stored locally in the `/logger_data` folder within your application directory.
