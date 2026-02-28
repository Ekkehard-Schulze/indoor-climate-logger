
# Attention: you need to rename this file to user_settings.py to activate it
#                        ------           -------------------    --------
# (copied from indoor-climate-logger.py code section master lines ~108 - ~179)

# name of this profile: Gundelfingen1
# purpose RPi PicoW or Pico2W http DS3231 location 220 meter above sea level


# ---------------------- user settings --------------------------
    
LOG_every_n_seconds = 300
LOGGER_name = ''
LOGGER_filename = ''

# select which busses / devices are queried on init
USE_i2c = True
USE_MHZ_19_CO2 = False
USE_ONE_WIRE = False
                            # Attention: For parasite power, I used the library modified by Schulze
                            # and an 820 Ohm (DS18x20) or 450 Ohm (MAX31850) pull-up resistor
                            # A 4700 Ohm pull-up resistor wasn't sufficient for four sensors, but it 
                            # worked for a single one.
REJECT_sensor_changes = True   # abort startup if sensors detected on init do not 
                               # match the top header of the existing log-file

WRITE_LOG_data_to_file = True
LOGGER_data_dir = 'logger_data'
LOG_EXCEPTIONS_to_file = True
SEPARATOR = '\t'

LOG_EXCPTIONS_filename = 'expeptions_log.txt'
VERBOSE = True           # data goto console print

USE_HTTP_server = True   # tested with Raspberry PicoW and Pico2W
IPV4 = '192.168.178.42'  
NETMASK = '255.255.255.0'
GATEWAY = '192.168.178.1' 
SET_RTC_from_NTP = True  # intended for microcontroller with WiFi. 
                          # Attention: RTC is the controllers build in RTC, NOT DS3231
                          # https://en.wikipedia.org/wiki/ISO_8601 
UTC_offset = +1           # UTC is 0, CET is 1, CEST is 2. Used only for NTP time request to set RTC'
TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}+01:00"  # use this style to indicate RTC time zone 
# TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z"     # for UTC      
# TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}"      # for time zone agnostic     

MONITOR_WIFI_connection = False  # not recommended, may lead to instability



USE_WATCHdog = False     # not recommended, may lead to instability 
                         # every 7 seconds in your code loops to prevent reset
                         # Attention: True led in combination with 
                         # MONITOR_WIFI_connection = True for Gundelfingen 
                         # CO2 logger to Error 205 and non-sceduled reboots

HOURS_between_reboots = 12  # used for HTTP-server to force cold-start and WiFi re-connect

HEIGHT_above_sea_level_in_meter = 260  # for normalizing local atmospheric pressure to sea level
MAX_log_file_size_in_bytes = 0  # zero means no file size limit set, this gets overwritten by the 
                  # microcontroller hardware auto-detection, or it may set her manually

USE_ALARM_wakeup_sleep = False  # only used for compatible hardware, e.g. RaspberryPi PicoW, 
                                # may require DS3231 clock
                                # not available on RPi Pico2 or Pico2_W, MS-Windows or 
                                # Linux, auto-set to false on Windows, linux
ALARM_SLEEP_HOLDOFF_TIME = 10   # seconds, used to get REPL access before sleep. This wastes battery. Better use button on startup to exit.
                                # alarm sleep, which  works on RPi Pico, not on Pico2

MAX_exception_file_size_bytes = 1_000_000 # may be changed by controller type detection

# -------------- end of user settings -----------------------------------