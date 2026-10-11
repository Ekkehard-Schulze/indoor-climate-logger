# ⚠️ CircuitPython Environment Only

This directory contains configurations explicitly designed for **CircuitPython** environments. It is not compatible with standard desktop CPython or standalone Linux systems without a proper hardware abstraction layer.

---

## 🔌 Required Hardware Drivers

Before running the script, you must download the **Adafruit CircuitPython Bundle** and manually copy the following driver files/folders into your device's local **`/lib`** folder:

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
* `adafruit_scd30`

---

## 🚀 Quick Setup

1. Connect your CircuitPython device via USB.
2. Open the device's root directory.
3. If it doesn't exist, create a folder named `lib`.
4. Drop the drivers listed above into the `/lib` folder.
5. Copy your application scripts into the root directory.
