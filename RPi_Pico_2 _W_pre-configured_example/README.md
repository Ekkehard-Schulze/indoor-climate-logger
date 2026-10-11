---
# Example configuration for Raspberry Pi Pico W

Copy this to the base directory of your microcontroller.
Then start the script `switch_RPiPico_to_USB_read_log_mode.py`
in the base directory of you folder, using the CPython interpreter
of your PC. This will do some renaming of files and folder,
restart your controller, connect to your WLAN, start logging
data and serve them on www. 

Retrive date here:

http://192.168.178.143/logger-data.tsv
http://192.168.178.143/expeptions_log.txt                                


--------------

Configured for
--------------

serving data using WLAN

- I2C thermosensors TMP117 and ADT7420

- 1-Wire thermosensors

### To get this going

- enter your WLAN credintials in `settings.toml`

- alternatively, you can set 

USE_HTTP_server = False


SET_RTC_from_NTP = False

in user_settings.py

to run this without WLAN on Raspberry Pi Pico or Raspberry Pi Pico2

###For trouble shooting 

connect to Thonny and start code py
from Thonny. This show you the connection to the WLAN,
the sensor discovery and the start of data logging.

You find your data on the device in the folder 'logger_data'.

For reading data via USB, the controller needs to start in
non-writing mode, see main readme for this.
