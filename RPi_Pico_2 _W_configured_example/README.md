---
# Example configuration for Raspberry Pi Pico W


Configured for
--------------

serving data using WLAN

- I2C thermosensors TMP117 and ADT7420

- 1-Wire thermosensors

### To get this going

- enter your WLAN credintials in settings.toml`

- alternatively, you can set 

USE_HTTP_server = False
SET_RTC_from_NTP = False

in user_settings.py

to run this without WLAN on Raspberry Pi Pico or Raspberry Pi Pico2


