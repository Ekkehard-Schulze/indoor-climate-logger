# 📂 Pre-Configured Examples

This directory contains ready-to-run example configurations for the **Indoor Climate Logger**, tailored for different hardware platforms and environments. 

Please navigate into the respective folder that matches your target system for specific setup and installation instructions.

---

## 💻 Supported Hardware Configurations

* **`Raspberry_Pi_Pico`**
  * Local sensor data logging directly onto a standard **Raspberry Pi Pico** or **Pico 2** microcontroller using CircuitPython.

* **`Raspberry_Pi_Pico_2 _W`**
  * Wireless configuration example for logging and serving climate data over WLAN using the **Raspberry Pi Pico 2 W** (or Pico W).

* **`Raspberry_Pi_3B`**
  * Local, persistent logging setup tailored for a Linux-based **Raspberry Pi 3B** single-board computer using native CPython (supporting native I2C and 1-Wire interfaces).

* **`MS-Windows_PC`**
  * Desktop environment configuration for a **Windows PC** utilizing external USB-to-I2C interface breakout hardware (such as FT232H, MCP2221, or a Pico U2IF bridge).

---

## 🚀 How to Use

1. **Choose your hardware platform** from the list above.
2. **Open the corresponding folder** to find the pre-configured scripts and a dedicated `README.md` guide.
3. Follow the steps inside to install dependencies (e.g., Python packages or CircuitPython libraries) and run the logger.
