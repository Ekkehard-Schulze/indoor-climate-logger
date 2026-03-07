#!/usr/bin/env python3
# This script can run under CPython3 and also under CircuitPython on microcontrollers

# You probably like to adjust the user settings starting in line 113 to your project's needs

# Attention: provide a user_settings.py file when using pylint, to avoid some complains
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=import-error
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=consider-using-f-string
# pylint: disable=import-outside-toplevel
# pylint: disable=unspecified-encoding
# flake8 --ignore=F541,E501 "indoor-climate-logger.py"

# Thonny command for RPi Pico stop write mode:
# import os; os.rename("/boot.py", "/boot.bak")


'''Indoor-climate-logger.py is a sensor data logger for either: 

 • CircuitPython (tested: 9.2.1) on a microcontroller,
   with I2C, 1Wire, and serial for the MH-Z19 CO2 sensor

 • CPython using the Adafruit Blinka Library running on MS-Windows 
   or Linux PCs or RaspberryPis
   CPython with Blinka  allows I2C bus communication, but not 1Wire.
   However on some linux systems, such as the RaspberyPi, a 1Wire kernel
   driver is available, which is supported here.

   For CPython install the required modules with the commands
   pip install -r CPython-requirements.txt
   
   For CircuitPython copy the respective sensor drivers for 
   your respective CircuitPython version into the /lib folder.
   The supported/required modules are 
   adafruit_register, adafruit_tmp117, adafruit_adt7410,   
   adafruit_bme280, adafruit_bme680, 
   adafruit_mlx90614, adafruit_tsl2561,
   adafruit_onewire, adafruit_ds3231, adafruit_ntp

Using CircuitPython a 2 x LED blink of microcontroller board-LED 
indicates that an un-cought exception occurred.

Sensors implemented with auto detect (auto-detect requires activation of the specific bus in this code)
------------------------------------
• i2c
  TMP117   temperature 0.1°C precision
  ADT7420  temperature 0.2°C precision
  mlx90614 temperature IR  0.5°C precision
  bme280   barometric pressure, humidity 3%, temperature ±1°C (0.5°C at 25°C) 
  bme680   barometric pressure, humidity 3%, temperature ±1°C 
  tsl2561  Lux

• 1Wire
  DS18B20  ±0.5°C Accuracy from -10°C to +85°C
  DS18S20  ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  DS1820   ±0.5°C Accuracy from -10°C to +85°C (obsolete)
  MAX31850 ±2°C for temperatures  -200°C to +700°C

• serial rx tx
   MH-Z19


RTC
------------------------------------
DS3231 is auto-detected and preferentially used, if the I2C-bus is enabled.


How to stop logging and get PC-write access on microcontroller USB-exposed drives, easy mode:
----------------------------------------------------------------------------------------------
run "switch_RPiPico_to_USB_read_log_mode.py" on the PC with microcontroller plugged to USB,
It useses REPL-code injection to rename boot.py to boot.bak.
replug to run in microcontroller-py-read-only = PC read-write mode

run "switch_RPiPico_to_write_log_mode.py" on the PC with microcontroller plugged to USB.
It renames boot.bak to boot.py and it moreover renames indoor-climate-logger.py to code.py.
Reset microcontroller to start logging.

How to stop logging and get PC-write access on microcontroller USB-exposed drives, elementary:
------------------------------------------------------------------------------------------------
plug to PC
start Thonny REPL, enter
import os
os.rename("/boot.py", "/boot.bak") # to prevent startup in py-write / PC read-only mode
reset microcontroller, e. g. by USB-replugging to run in 
microcontroller-py-read-only = PC read-write mode

Howto fix one-wire operations in Adafruit-library for parasite power mode on microcontrolers
--------------------------------------------------===================-----------------------
I modified the convert function in the Adafruit library, see /lib/schulze_one_wire_temperature.py
moreover the pullup needed be lower than the assumed standard of 4700 Ohm:
for DS18x20  820 Ohm pullup for 3V3
for MAX31850 450 Ohm pullup for 3V3
(the non-modified Adafruit library resulted for DS18B20 in false temperature
readings of 85°C, which is the default power-up init value of the sensor.
This indicates a non-sufficient power supply for the temperature conversion,
the MAX31850 gave ~50°C readings in room temperature)
I think that the micropython 1wire driver does not cover correctly parasitic power,
however the Arduino implementation does. The same poblems seems to be in the Linux kernel driver.
'''

import os
import sys
import time

__version__ = "2.0.0"

# ---------------------- user settings --------------------------

try:
    from user_settings import * 

except ImportError:  # if no user_settings.py file is found the settings below are used:
                    # by the way: Circuit Python does not know ModuleNotFoundError,
                    # ImportError is an upstream generic Error
    # here are user-settings for  RPi PicoW http NTP-time location 220 meter above sea level
    # use this code block as master to derive further user settings
    
    LOG_every_n_seconds = 300
    LOGGER_name = 'MHZ_19_CO2_logger'
    LOGGER_filename = 'MHZ_19_CO2_log.tsv'

    # select which busses / devices are queried on init
    USE_i2c = True
    USE_MHZ_19_CO2 = True
    USE_ONE_WIRE = True
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
    UTC_offset_hours = +1     # UTC is 0, CET is 1, CEST is 2. Used only for NTP time request to set RTC'
    TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}+01:00"   

    # TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z"   # for UTC      
    # TIME_FORMAT_PATTERN = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}"   # for time zone agnostic     
    
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


# ---------- just here for pylint
i2c = None
uart = None
ipv4 = None
netmask = None
gateway = None
pool = None
ds3231_rtc = None

# ------------ 
USE_ONE_WIRE_temperature_Linux_Kernel = None
USE_ONE_WIRE_temperature_Adafruit_CircuitPy = None


# -------------- board and python implementation specific settings ----------------

if sys.implementation.name == "cpython":   # auto-switch to PC-mode for MS_Windows or Linux
    import argparse
    import platform

    if USE_ONE_WIRE:
        if platform.system() == 'Linux':
            USE_ONE_WIRE_temperature_Linux_Kernel = True
            USE_ONE_WIRE_temperature_Adafruit_CircuitPy = False
        else:
            raise Exception('1Wire with CPython requires Linux and the 1Wire kernel driver.')
    if USE_MHZ_19_CO2:
        raise Exception('MH-Z19 not implemented in CPython.')
    if USE_HTTP_server:
        raise Exception('http-Server not imlemented in CPython.')
    if SET_RTC_from_NTP:
        raise Exception('NTP-time not imlemented in CPython. Use python time.')

    def set_i2c_environment_vars_for_Blinka(mode=1):
        '''prepare for adafruit-blinka on cpython PC'''

        def Win_FT232H_with_ftdi_driver_present():
            '''circuit python requires libusbK driver. Win updates replace this with FTDI driver.
            This is to detect this failure reason'''
            import ftd2xx     # pip install ftd2xx # this is a FTDI module for python 3, not a CircuitPython module
            try:
                dl = ftd2xx.open(0)           # Open first FTDI device
                # FT232H yields {'type': 8, 'id': 67330068, 'description': b'Single RS232-HS', 'serial': b''}
                ftdi232h_has_ftdi_driver = dl.getDeviceInfo()['id'] == 67330068
            except ftd2xx.ftd2xx.DeviceError:
                ftdi232h_has_ftdi_driver = False
            return ftdi232h_has_ftdi_driver

        USB_IC_selector_for_Blinka = (
            (  # set NONE of these to "1" to select Rpi3B, all  to ""
                ("BLINKA_FT232H", ""),  # TMP117 fails when combined with ADT7420
                ("BLINKA_MCP2221", ""),  # Adafruit ADT7410 driver fails
                ("BLINKA_U2IF", ""),  # RPi Pico firmware u2if, Adafruit ADT7410 driver fails
            ),
            (  # set one of these to "1" to select, all other to ""
                ("BLINKA_FT232H", "1"),  # TMP117 fails when combined with ADT7420
                ("BLINKA_MCP2221", ""),  # Adafruit ADT7410 driver fails
                ("BLINKA_U2IF", ""),  # RPi Pico firmware u2if, Adafruit ADT7410 driver fails
            ),
            (  # set one of these to "1" to select, all other to ""
                ("BLINKA_FT232H", ""),  # TMP117 fails when combined with ADT7420
                ("BLINKA_MCP2221", "1"),  # Adafruit ADT7410 driver fails
                ("BLINKA_U2IF", ""),  # RPi Pico firmware u2if, Adafruit ADT7410 driver fails
            ),
            (  # set one of these to "1" to select, all other to ""
                ("BLINKA_FT232H", ""),  # TMP117 fails when combined with ADT7420
                ("BLINKA_MCP2221", ""),  # Adafruit ADT7410 driver fails
                ("BLINKA_U2IF", "1"),  # RPi Pico firmware u2if, Adafruit ADT7410 driver fails
            ),
        )

        if platform.system() == 'Windows':
            for blinka_ic in USB_IC_selector_for_Blinka[mode]:
                os.environ[blinka_ic[0]] = blinka_ic[1]  # put IC-specifying env var in py code instead of administrating the environment in windows
            if ("BLINKA_FT232H", "1") in USB_IC_selector_for_Blinka:  # if FT232H IC is selected reject FTDI driver, we need libusbK
                if Win_FT232H_with_ftdi_driver_present():
                    sys.exit('\nno libusbK driver for FT232H present. Use Zadig first.\n')
        elif platform.system() == 'Linux':
            for blinka_ic in USB_IC_selector_for_Blinka[mode]:
                os.environ[blinka_ic[0]] = blinka_ic[1]  # put IC-specifying env var in py code instead of administrating the
        elif platform.system() == 'Darwin':  # macOS
            for blinka_ic in USB_IC_selector_for_Blinka[mode]:
                os.environ[blinka_ic[0]] = blinka_ic[1]  # put IC-specifying env var in py code instead of administrating the

    parser = argparse.ArgumentParser(
        description="Ekkehard's environment logger for CPython on PC or RaspberryPi using Blinka, \nor CircuitPython on RaspberryPi Pico or PicoW with http server",
        epilog="Have fun with precision sensors",
        formatter_class=argparse.RawTextHelpFormatter,
    )  # init object

    # ---------- define arguments
    parser.add_argument('-s', '--LOG_every_n_seconds', default=str(LOG_every_n_seconds), help='Log every second')  # string
    parser.add_argument('-u', '--USB_IC', default="0", help='0:RPi 1: FT232H  2: MCP2221  3: RPi Pico U2IF')  # string
    parser.add_argument("-nf", "--do_not_write_log_file", default=False, help="write no logfile", action="store_true")  # boolean argparse
    # --------------  collect arguments
    args = parser.parse_args()

    # ------- poke arguments
    if args.USB_IC == "0" and not platform.system() == 'Linux' and not "ARM" in platform.machine().upper():
        parser.print_help()
        sys.exit("You have to choose an USB-Ic.")    
    LOG_every_n_seconds = int(args.LOG_every_n_seconds, 0)
    WRITE_LOG_data_to_file = not args.do_not_write_log_file
    if args.USB_IC not in '0123':
        sys.exit('-u argument must either be 0, 1, 2, or 3\n')
    set_i2c_environment_vars_for_Blinka(int(args.USB_IC))
    print("\nUsing PC-Adafruit-Blinka mode\n")
    import board

elif sys.implementation.name == "circuitpython":
    import board
    USE_ONE_WIRE_temperature_Linux_Kernel = False
    USE_ONE_WIRE_temperature_Adafruit_CircuitPy = True
    USE_ALARM_wakeup_sleep = board.board_id == "raspberry_pi_pico"
    if board.board_id in ["raspberry_pi_pico", "raspberry_pi_pico2"]:
        if board.board_id == "raspberry_pi_pico": # tested using CircuitPython 8.x
            MAX_log_file_size_in_bytes = 360_000  # use <45% of free flash size to prevent exhaustion of flash storage and to allow file duplication for truncation
        elif board.board_id == "raspberry_pi_pico2": # use CircuitPython 9.x
            MAX_log_file_size_in_bytes = 1_100_000  # use <45% of free flash size to prevent exhaustion of flash storage and to allow file duplication for truncation
        time.sleep(1.5)  # may be required for RPi Pico battery power, see https://www.youtube.com/watch?v=mCYB9tjsF0I Fix A Raspberry Pi Pico That Won't Run Code TUTORIAL

    elif board.board_id in ["raspberry_pi_pico_w", "raspberry_pi_pico2_w"]:

        if board.board_id == "raspberry_pi_pico_w": # use CircuitPython 8.x, not >= 9.x due to memory shortage
            MAX_log_file_size_in_bytes = 150_000  # use <45% of free flash size to prevent exhaustion of flash storage and to allow file duplication for truncation
        elif board.board_id == "raspberry_pi_pico2_w": # tested using CircuitPython 9.x
            MAX_log_file_size_in_bytes = 1_000_000  # use <45% of free flash size to prevent exhaustion of flash storage and to allow file duplication for truncation
        time.sleep(1.5)  # may be required for RPi Pico battery power, see https://www.youtube.com/watch?v=mCYB9tjsF0I Fix A Raspberry Pi Pico That Won't Run Code TUTORIAL

elif sys.implementation.name == "micropython":
    sys.exit('\nThis code is for circuitpython or CPython with Adafruit-blinka. It does not run on micropython\n')

# -------------- end of  board and python implementation specific settings ----------------


# ============ sensor objects for logger. each sensor object handles all individual sensors of its kind in a single object instance   =====#
# each class needs to provide __init__(), get_sensor_headers(), and get_measurement_str(

if USE_ONE_WIRE_temperature_Adafruit_CircuitPy:
    class one_wire_temperature_Adafruit_CircuitPy():
        ''' ----------- sensor 1wire specific code for logger  ------------
        stores list of responding 1Wire sensors.
        Retrieves sensor names and measurements of all sensors at once.
        '''
        filename = r"1wire_temperature_log.tsv"

        def __init__(self, ow_busl):
            self.LOGGER_name = "1wire_logger"
            self.my_DS18X20_MAX31850_sensors = [schulze_one_wire_temperature.DS18X20_MAX31850(ow_busl, ds) for ds in ow_bus.scan()]
            self.my_DS18X20_MAX31850_sensors.sort(key=lambda x: x.es_name, reverse=False)

        def get_sensor_headers(self):
            return ''.join([SEPARATOR + sens.es_name  for sens in self.my_DS18X20_MAX31850_sensors])

        def get_single_measurement(self, sens):
            return "{:.2f}".format(sens.temperature)

        def get_measurement_str(self):
            return ''.join([SEPARATOR + self.get_single_measurement(sens)  for sens in self.my_DS18X20_MAX31850_sensors])

if USE_ONE_WIRE_temperature_Linux_Kernel:
    class one_wire_temperature_Linux_kernel():
        ''' ----------- sensor 1wire specific code for logger  ------------
        stores list of responding 1Wire sensors.
        Retrieves sensor names and measurements of all sensors at once.
        Attention: log_1wire.py RaspberryPi Kernel driver only see  Ekkehard's utility dir
        '''
        filename = r"1wire_temperature_log.tsv"

        def __init__(self):
            import glob
            self.LOGGER_name = "1wire_logger"
            self.base_dir = '/sys/bus/w1/devices/'
            self.device_folder_list = glob.glob(self.base_dir + '28*')

        def generate_name(self, device_folderl):
            '''Using 8-bit sum heren, NOT crc8. Saves the purpose as well'''
            hexl = device_folderl.split('/')[-1].replace('-', '')
            bbb = bytearray.fromhex(hexl)
            return 'DS' + str(sum(bbb) % 256)

        def read_temp_raw(self, device_folderl):
            device_file = device_folderl + '/w1_slave'
            with open(device_file, 'r') as f:
                lines = f.readlines()
            return lines

        def get_sensor_headers(self):
            header = ''
            for dd in self.device_folder_list:
                header += SEPARATOR + self.generate_name(dd) 
            return header

        def get_measurement_str(self):
            out_str = ''
            for device_folder in self.device_folder_list:
                temp_c = 0
                lines = self.read_temp_raw(device_folder)
                while lines[0].strip()[-3:] != 'YES':
                    time.sleep(0.2)
                    lines = self.read_temp_raw(device_folder)
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos + 2:]
                    temp_c = float(temp_string) / 1000.0
                out_str += f'{SEPARATOR}{temp_c:.2f}'
            return out_str


if USE_i2c:

    class ADT7420():
        ''' ----------- sensor ADT7420 specific code for logger  ------------
        operates on a list of all four possible sensors and acts on the responding (installed) ones.
        distinguishes ADT7420 from TMP117, both have the same I2C address space.
        '''
        filename = r"ADT7420_log.tsv"

        def __init__(self):

            self.LOGGER_name = "ADT7420_logger"

            self.my_sensor_names = ['ADT1', 'ADT2', 'ADT3', 'ADT4', ]

            self.my_sensors = [None, None, None, None]

            import adafruit_adt7410
            for n, _ts in enumerate(self.my_sensors):
                try:
                    if not TMP117_es.is_TMP117(0x48 + n):
                        self.my_sensors[n] = adafruit_adt7410.ADT7410(i2c, address=0x48 + n)
                        self.my_sensors[n].high_resolution = True
                except ValueError:
                    pass

        def get_sensor_headers(self):
            rstr = ''
            for n, ts in enumerate(self.my_sensors):
                if ts is not None:
                    rstr += SEPARATOR + self.my_sensor_names[n] 
            return rstr

        def get_single_measurement_fastest(self, tsl):
            return "{:.2f}".format(tsl.temperature)

        def get_single_measurement(self, tsl):
            '''read with 8x averaging and 250 ms delay'''
            AVERAGES = 8
            t_tmp = 0
            for _ in range(AVERAGES):
                t_tmp += tsl.temperature
                time.sleep(0.250)
                if USE_WATCHdog:
                    watchdog.feed()
            return f"{t_tmp / AVERAGES:.2f}"

        def get_measurement_str(self):
            measurement_str = ''
            for ts in self.my_sensors:
                if ts is not None:
                    measurement_str += SEPARATOR + self.get_single_measurement(ts) 
            return measurement_str

    class TMP117_es():
        '''sensor TMP117 specific code for logger handling 4 sensors

        Attention: object name TMP117 is already used by Adafruit

        Operates on a list of all four possible sensors and acts on the responding (installed) ones.
        distinguishes TMP117 from ADT7420, both have the same I2C address space.
        '''

        filename = "TMP117_log.tsv"

        def __init__(self):
            self.LOGGER_name = "TMP117_logger"

            self.my_sensor_names = ['TMP1', 'TMP2', 'TMP3', 'TMP4', ]

            self.my_sensors = [None, None, None, None]

            from adafruit_tmp117 import TMP117, AverageCount, _ONE_SHOT_MODE
            self._ONE_SHOT_MODE = _ONE_SHOT_MODE
            for n, _ts in enumerate(self.my_sensors):
                try:
                    if TMP117_es.is_TMP117(0x48 + n):
                        self.my_sensors[n] = TMP117(i2c, address=0x48 + n)
                        self.my_sensors[n].averaged_measurements = AverageCount.AVERAGE_64X
                except ValueError:
                    pass

        def get_sensor_headers(self):
            rstr = ''
            for n, ts in enumerate(self.my_sensors):
                if ts is not None:
                    rstr += SEPARATOR + self.my_sensor_names[n] 
            return rstr

        def get_single_measurement_obsolete_fails(self, tsl):
            '''20250423 esmod attempt to avoid crash of RPi Pico2_W logger when reading TMP117
            Logger RPi Pico2W mit TMP117 bleibt jeweils nach einigen Stunden und ein paar dutzend
            Datenpunkten ohne Fehlermeldung stehen, unabhängig davon welcher TMP2 Sensor
            verwendet wurde. Die Ursache fand sich in der Temperaturabfrage der TMP117 CircuitPython
            Library. In "_set_mode_and_wait_for_measurement()" wird eine 1 ms delay ready-poll
            -loop  mit Abfrage von "read_status()" verwendet. Diese Loop durch ein konstantes
            2500 ms delay, gefolgt von Lesen der Temperatur ohne Statusabfrage ersetzt ergibt ein
            stabiles Verhalten. Offenbar endet diese loop manchmal in einer Endlosschleife
            stabiles Verhalten. Offenbar endet diese loop manchmal in einer Endlosschleife
            '''
            return "{:.2f}".format(tsl.take_single_measurement())

        def get_single_measurement(self, tsl):
            '''2500 ms delay instead of poll status every 1 ms'''
            tsl._mode = self._ONE_SHOT_MODE
            if USE_WATCHdog:
                watchdog.feed()
            time.sleep(2.500)
            if USE_WATCHdog:
                watchdog.feed()
            return "{:.2f}".format(tsl._read_temperature())

        def get_measurement_str(self):
            measurement_str = ''
            for ts in self.my_sensors:
                if ts is not None:
                    measurement_str += SEPARATOR + self.get_single_measurement(ts) 
            return measurement_str

        @classmethod
        def is_TMP117(cls, addrl):
            TMP117_Device_ID_register = 0x0F
            val = 0
            try:
                while not i2c.try_lock():
                    pass
                i2c.writeto(addrl, bytes([TMP117_Device_ID_register]))
                result = bytearray(2)
                i2c.readfrom_into(addrl, result)
                val = ((result[0] << 8) + result[1]) & 0b0000111111111111  # 16 bit, erase revision nr bits
            except:
                pass
            finally:
                i2c.unlock()
            return val == 0x117

    class mlx90614():
        ''' ----------- Ir temp sensor mlx90614 single sensor specific code for logger  -------'''

        filename = "mlx90614_log.tsv"

        def __init__(self):
            import adafruit_mlx90614
            self.mlx = adafruit_mlx90614.MLX90614(i2c)
            self.LOGGER_name = "IR temperature logger"
            self.my_sensor_names = ['Mlx_temp', 'Mlx_ir_temp']

        def get_sensor_headers(self):
            return SEPARATOR + SEPARATOR.join(self.my_sensor_names) 

        def get_measurement_str(self):
            return SEPARATOR + "{:.2f}".format(self.mlx.ambient_temperature) + SEPARATOR + "{:.2f}".format(self.mlx.object_temperature) 

    class tsl2561():
        ''' ----------- lux sensor tsl2561 specific code for logger handling one sensor.
        Attention: 10 seconds per measurement variant (using 10x average)  ------------'''

        filename = "Lux_log.tsv"

        def __init__(self):
            import adafruit_tsl2561
            self.LOGGER_name = "Lux_logger"
            self.my_sensor_names = ['Lux', ]
            self.tsl = adafruit_tsl2561.TSL2561(i2c)    # Create the TSL2561 instance, passing in the I2C bus
            self.tsl.enabled = True                     # Create the TSL2561 instance, passing in the I2C bus
            time.sleep(0.15)                            # wait for finish of sensor init, required?
            self.tsl.gain = 0                           # Set gain 0=1x, 1=16x
            self.tsl.integration_time = 2               # Set integration time (0=13.7ms, 1=101ms, 2=402ms, or 3=manual)
            self.averages = 1                           # number of repeated and averaged measuremens
            self.delay = 0                              # delay between measurements

        def get_sensor_headers(self):
            return SEPARATOR + SEPARATOR.join(self.my_sensor_names) 

        def get_single_measurement(self, tsl):
            ''' average of 10 lux measurements with 1 second delay'''
            dlist = []
            for _n in range(0, self.averages):
                lux = tsl.lux
                if lux is not None:
                    dlist.append(lux)
                else:
                    print('Overflow?')
                time.sleep(self.delay)
            return round(sum(dlist) / len(dlist)) if len(dlist) > 0 else ""

        def get_measurement_str(self):
            return SEPARATOR + str(self.get_single_measurement(self.tsl)) 

    class bme280():
        ''' ----------- sensor BME280 specific code handling one sensor for logger Achtung: 260 Meter Höhe in global var ------------'''

        filename = "BME280_log.tsv"

        def __init__(self):
            from adafruit_bme280 import basic as adafruit_bme280
            self.LOGGER_name = "clima logger"
            self.my_sensor_names = ['BME_temp', 'BME_humidity', 'BME_pressure']
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

        def get_sensor_headers(self):
            return SEPARATOR + SEPARATOR.join(self.my_sensor_names) 

        @classmethod
        def sea_barometric_pressure_estimate(cls, local_pressure, local_temperature, local_heigt_above_sea_level):
            ''' https://gist.github.com/cubapp/23dd4e91814a995b8ff06f406679abcf  '''
            return local_pressure + ((local_pressure * 9.80665 * local_heigt_above_sea_level) / (287 * (273 + local_temperature + (local_heigt_above_sea_level / 400))))

        def get_measurement_str(self):
            temp = self.bme280.temperature
            pressure = self.bme280.pressure
            sea_level_pressure = bme280.sea_barometric_pressure_estimate(pressure, temp, HEIGHT_above_sea_level_in_meter)  # 260 ist Höhe von Gundelfingen
            return (
                SEPARATOR + "{:.2f}".format(temp) 
                + SEPARATOR + "{:.1f}".format(self.bme280.humidity) 
                + SEPARATOR + "{:.1f}".format(sea_level_pressure) 
            )

    class bme680():
        ''' ----------- sensor BME680 specific code handling one sensor for logger Achtung: 260 Meter Höhe in global var ------------'''

        filename = "BME680_log.tsv"

        def __init__(self):
            import adafruit_bme680
            self.LOGGER_name = "clima air logger"
            self.my_sensor_names = ['BME_temp', 'BME_humidity', 'BME_pressure', 'BME_air']
            self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77, debug=False)
            self.bme680.sea_level_pressure = 1013.25

        def get_sensor_headers(self):
            return SEPARATOR + SEPARATOR.join(self.my_sensor_names) 

        @classmethod
        def sea_barometric_pressure_estimate(cls, local_pressure, local_temperature, local_heigt_above_sea_level):
            ''' https://gist.github.com/cubapp/23dd4e91814a995b8ff06f406679abcf  '''
            return local_pressure + ((local_pressure * 9.80665 * local_heigt_above_sea_level) / (287 * (273 + local_temperature + (local_heigt_above_sea_level / 400))))

        def get_measurement_str(self):
            for _ in range(20):  # delay to get last value
                temp = self.bme680.temperature
                pressure = self.bme680.pressure
                sea_level_pressure = bme680.sea_barometric_pressure_estimate(pressure, temp, HEIGHT_above_sea_level_in_meter)  # 260 ist Höhe von Gundelfingen
                air = self.bme680.gas
                # time.sleep(0.7)

            return (
                SEPARATOR + "{:.2f}".format(temp) 
                + SEPARATOR + "{:.1f}".format(self.bme680.relative_humidity) 
                + SEPARATOR + "{:.1f}".format(sea_level_pressure)
                + SEPARATOR + "{:.1f}".format(air) 
            )

if USE_MHZ_19_CO2:

    class MHZ_19():
        ''' ----------- CO2 sensor MH-Z19 code for logger  ------------'''
        filename = r"MHZ_19_CO2_log.tsv"

        def __init__(self):
            self.LOGGER_name = "MHZ_19_CO2_logger"
            self.my_sensor_names = ['CO2',]
            self.init_phase_is_on = True  # during the minutes long init phase the MH-Z19 gives 410 ppm as a read

        def get_sensor_headers(self):
            return SEPARATOR + SEPARATOR.join(self.my_sensor_names) 

        @classmethod
        def get_single_measurement(cls):
            CO2_ppm = 0
            max_attempts = 5
            attempts = 0
            while True:
                attempts += 1
                uart.write(bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]))
                time.sleep(1)
                result = []

                try:
                    for _i in range(0, 9):
                        result.append(uart.read(1))
                        time.sleep(0.1)
                    if None not in result and len(result) == 9:
                        checksum = (0xFF - ((ord(result[1]) + ord(result[2]) + ord(result[3]) + ord(result[4]) + ord(result[5]) + ord(result[6]) + ord(result[7])) % 256)) + 0x01
                        if checksum == ord(result[8]):
                            CO2_ppm = ord(result[2]) * 256 + ord(result[3])

                except Exception as el:
                    if LOG_EXCEPTIONS_to_file:
                        with open(LOG_EXCPTIONS_filename, "a") as except_log_filel:
                            try:
                                except_log_filel.write(get_time_date_str())
                            except:
                                pass
                            except_log_filel.write('MH-Z19 exception, attempt nr. ' + str(attempts) + '\n')
                            except_log_filel.write(str(el) + ' ... in MH-Z19 get_single_measurement.\n')
                            # log_file.write(str(e)+' in line '+str(e.__traceback__.tb_lineno)+'\n') # not available in micropython
                            # log_file.write(str(dir(e))+'\n')
                            # log_file.write(str(dir(e.__traceback__))+'\n') # ........ no way to log the line number in python
                                                                            # no traceback.format_exc() in micropython, this would require a re-compile! <<<<<<<<<<<<< !!!, see:
                                                                            # https://github.com/micropython/micropython/issues/5110
                    elif attempts >= max_attempts:
                        raise Exception('MHZ_19 reading failed') from el
                if CO2_ppm > 0 or attempts >= max_attempts:
                    break
            return CO2_ppm

        def get_measurement_str(self):
            CO2val = MHZ_19.get_single_measurement()
            if self.init_phase_is_on and CO2val not in (0, 410):  # first real value ends init_phase
                self.init_phase_is_on = False              # switch instance boolean here, because get_measurement_str is an instance method
            if self.init_phase_is_on and CO2val == 410:    # whereas MHZ_19.get_single_measurement() is a class method
                CO2valstr = ''
            elif CO2val == 0:
                CO2valstr = ''
            else:
                CO2valstr = str(CO2val)
            return SEPARATOR + CO2valstr 


# ============================= end sensor objects ===============================

# --- utilities, not used from a lib not to spoil the convenient single-file usage option 
# on Win or Linux PC running CPython

def file_exists(fnamel):
    ''''workaround for 'from os.path import exists' which is not available in circuit/micro python'''
    try:
        with open(fnamel, "r") as _f:
            exists = True
    except OSError:  # open failed
        exists = False
    return exists


def dir_exists(dirnamel):  # workaround: from os.path import exists # not available in circuit/micro python
    old_dir = os.getcwd()
    try:
        os.chdir(dirnamel)
        exists = True
    except OSError:  # chdir failed
        exists = False
    finally:
        os.chdir(old_dir)
    return exists


def reset_microcontroller(reset_delay=5):
    import microcontroller
    print(f"restarting in {reset_delay} seconds ..")
    time.sleep(reset_delay)
    microcontroller.reset()


def truncate_log_top(log_file_namel, size_limit, n_lines_to_delete=288):
    '''Delete top part of log data in order to limit file size.
    The idea is to prune oldest data e.g. once a day'''
    if 0 < size_limit < os.stat(log_file_namel)[6]:  # micropython uses plain tupel, CPython uses named tupel, which is downwards compatible to plain tupel
        # basename, _extension = os.path.splitext(log_file_namel) # not available in micropython
        # bak_file_name = basename+'.bak'
        bak_file_name = log_file_namel[:-4] + '.bak'
        if file_exists(bak_file_name):
            os.remove(bak_file_name)
        os.rename(log_file_namel, bak_file_name)
        with open(bak_file_name, 'r') as oldfile, open(log_file_namel, 'w') as newfile:
            for n, l in enumerate(oldfile):
                if n == 0 or n > n_lines_to_delete:  # keep header, trucate top n data lines
                    newfile.write(l)
        os.remove(bak_file_name)


def get_time_date_str():
    if not DS3231_present:
        now = (
            time.localtime()
        )  # local time on PC. This leads to a discrepancy in the dataset.
    else:
        now = ds3231_rtc.datetime
    return TIME_FORMAT_PATTERN.format(
        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec
    )


# --------- main  ----------------------------
# init exceptions log file
if MAX_log_file_size_in_bytes:
    max_exception_file_size = int(MAX_log_file_size_in_bytes * 0.05)
else:
    max_exception_file_size  = MAX_exception_file_size_bytes
if (LOG_EXCEPTIONS_to_file or WRITE_LOG_data_to_file) and LOGGER_data_dir != '' and not dir_exists(LOGGER_data_dir):
    os.mkdir(LOGGER_data_dir)
if not file_exists(LOGGER_data_dir + os.sep + LOG_EXCPTIONS_filename) and LOG_EXCEPTIONS_to_file:
    with open(LOGGER_data_dir + os.sep + LOG_EXCPTIONS_filename, "a") as except_log_file:
        except_log_file.write("Exceptions raised:\n")

try:  # -------- outer error handler loop -------------------
    # ----------------- init hardware driver ----------------------------------
    # ------------ init circuitpython/blinka specifics -------------------------------

    # import board # happened at different places above
    import busio

    if USE_ALARM_wakeup_sleep:
        import alarm
    if USE_ONE_WIRE_temperature_Adafruit_CircuitPy:
        from adafruit_onewire.bus import OneWireBus
        import schulze_one_wire_temperature

    # --------------- handle board specific bus inits ------------------------------------------
    if board.board_id == "raspberry_pi_pico":
        if USE_i2c:
            i2c = busio.I2C(board.GP5, board.GP4, frequency=100000)  # Circuit py default is 400000
        if USE_MHZ_19_CO2:
            uart = busio.UART(board.GP16, board.GP17, baudrate=9600, timeout=1)  # RPi Pico, timeout is essential for MH-Z19
        if USE_ONE_WIRE_temperature_Adafruit_CircuitPy:
            ow_bus = OneWireBus(board.GP28)

    elif board.board_id in ["raspberry_pi_pico_w", "raspberry_pi_pico2_w"]:
        if USE_i2c:
            i2c = busio.I2C(board.GP5, board.GP4, frequency=100000)  # Circuit py default is 400000
        if USE_MHZ_19_CO2:
            uart = busio.UART(board.GP16, board.GP17, baudrate=9600, timeout=1)  # RPi Pico, timeout is essential for MH-Z19
        if USE_ONE_WIRE_temperature_Adafruit_CircuitPy:
            ow_bus = OneWireBus(board.GP28)

    else:
        if USE_i2c:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # Circuit py default is 400000
        if USE_MHZ_19_CO2:
            uart = busio.UART(board.TX, board.RX, baudrate=9600)

    DS3231_present = False  # default, gets automatically overwritten if clock is detected

    if USE_i2c:
        # -------------- scan i2c bus --------------------------------
        while not i2c.try_lock():  # required for scan on microcontroller boards
            pass
        i2c_devices = [hex(x) for x in i2c.scan()]
        # Unlock the I2C bus when finished.  Ideally put this in a try-finally!
        i2c.unlock()

        i2c_present_str = '\ni2c device(s) '
        for d in i2c_devices:
            i2c_present_str += d + ' '
        # print(i2c_present_str)

        # ------------ tcxo clock DS3221 if present ---------------------
        DS3231_present = '0x68' in i2c_devices
        if DS3231_present:
            import adafruit_ds3231
            ds3231_rtc = adafruit_ds3231.DS3231(i2c)
            print('Using DS3231 clock')
            # Attention: the following commands lead to failure to alarm-restart !!!
            # import rtc
            # rtc = rtc.RTC()
            # rtc.datetime = ds3231_rtc.datetime # for internal rtc without battery backup set rts to DS3231 time. The will yield correct time.localtime()

    # ----------------- init sensor objects if sensor presence is detected -----------------------------
    my_sensors = []  # list of sensor objects. Only sensors responding on init are listed here.

    if USE_MHZ_19_CO2:
        if MHZ_19.get_single_measurement() > 0:
            my_sensors.append(MHZ_19())

    if USE_i2c:
        if (
            ("0x48" in i2c_devices and TMP117_es.is_TMP117(0x48))
            or ("0x49" in i2c_devices and TMP117_es.is_TMP117(0x49))
            or ("0x4a" in i2c_devices and TMP117_es.is_TMP117(0x4A))
            or ("0x4b" in i2c_devices and TMP117_es.is_TMP117(0x4B))
        ):
            my_sensors.append(TMP117_es())

        if (
            ("0x48" in i2c_devices and not TMP117_es.is_TMP117(0x48))
            or ("0x49" in i2c_devices and not TMP117_es.is_TMP117(0x49))
            or ("0x4a" in i2c_devices and not TMP117_es.is_TMP117(0x4A))
            or ("0x4b" in i2c_devices and not TMP117_es.is_TMP117(0x4B))
        ):
            my_sensors.append(ADT7420())

        if '0x5a' in i2c_devices:
            my_sensors.append(mlx90614())

        if '0x76' in i2c_devices:
            my_sensors.append(bme280())

        if '0x77' in i2c_devices:
            my_sensors.append(bme680())
            # dummy reading because the first reading is wrong 100% humidity pressure 729.7
            _ = my_sensors[-1]. get_measurement_str()
            time.sleep(1)

        if '0x39' in i2c_devices:
            my_sensors.append(tsl2561())

    if USE_ONE_WIRE_temperature_Linux_Kernel:
        my_sensors.append(one_wire_temperature_Linux_kernel())

    if USE_ONE_WIRE_temperature_Adafruit_CircuitPy:
        my_sensors.append(one_wire_temperature_Adafruit_CircuitPy(ow_bus))

    LOGGER_filename = my_sensors[0].filename if LOGGER_filename == '' else LOGGER_filename  # get name from sensor object if no othre name waf pre-defined

    # ------ configure and start http server -----------------
    if USE_HTTP_server or SET_RTC_from_NTP:

        # www code parts for RapberryPi PicoW
        # --------------------------------------
        # es merged www code from
        # a) example file name: httpserver_start_and_poll.py
        # shows how to submit a static index.html
        # b) https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
        # reads DS18x20 and makes a www page with buttons

        import ipaddress
        import socketpool
        import wifi
        ipv4 = ipaddress.IPv4Address(IPV4)
        netmask = ipaddress.IPv4Address(NETMASK)
        gateway = ipaddress.IPv4Address(GATEWAY)
        wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)
        # base64 usage this led to Exceptions in main loop and could not be used
        # wifi.radio.connect(
            # base64.b64decode(os.getenv("CIRCUITPY_WIFI_SSID")).decode("utf-8"),    # added char = to have string len a multiple of 4. This decodes properly
            # base64.b64decode(os.getenv("CIRCUITPY_WIFI_PASSWORD")).decode("utf-8"), #
        # )
        wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
        print("Connected to WiFi")
        pool = socketpool.SocketPool(wifi.radio)

    if USE_HTTP_server:
        # import base64   # this led to Exceptions in main loop and could not be used
        from adafruit_httpserver import (
            Server,
            # REQUEST_HANDLED_RESPONSE_SENT,
            Request,
            FileResponse,
        )
        server = Server(pool, LOGGER_data_dir, debug=True)

        @server.route("/")
        def base(request: Request):
            """
            Serve the default index.html file.
            """
            return FileResponse(request, LOGGER_filename)  # instead of index html

        server = Server(pool, LOGGER_data_dir, debug=True)  # use root dir

        print("starting server..")
        # startup the server
        try:
            server.start(str(wifi.radio.ipv4_address))
            print("Serving http://%s:80//%s" % (wifi.radio.ipv4_address, LOGGER_filename))
        #  if the server fails to begin, restart the RPi Pico w
        except OSError:
            if sys.implementation.name == "circuitpython":
                reset_microcontroller()
        reboot_counter_for_server = int((HOURS_between_reboots * 60 * 60) / LOG_every_n_seconds)  # 12h reboot counter to renew connection

    if SET_RTC_from_NTP:  # Attention: RTC is the controllers build in RTC, NOT DS3231
        import adafruit_ntp
        from rtc import RTC
        rtc = RTC()
        rtc.datetime = adafruit_ntp.NTP(pool, tz_offset=UTC_offset_hours, cache_seconds=3600).datetime

    # --------------- collect all sensor names from sensor objects -------------------------------

    sens_header = ''.join([sensor.get_sensor_headers()  for sensor in my_sensors])

    print('\nSensor(s) ' + sens_header.replace(SEPARATOR, ' '))

    LOGGER_name = my_sensors[0].LOGGER_name if LOGGER_name == '' else LOGGER_name  # get name from sensor object if no other name was pre-defined

    # ------------------- init log file and log dir  ------------------------
    if LOGGER_data_dir != '' and WRITE_LOG_data_to_file:
        if not dir_exists(LOGGER_data_dir):
            os.mkdir(LOGGER_data_dir)

    def write_header_line():
        with open(LOGGER_data_dir + os.sep + LOGGER_filename, "a") as log_filel:  # use append mode to prevent deleting data. Append makes a new file if none exists.
            log_filel.write(
                "logger-id" + SEPARATOR + "Date_time" + sens_header + "\n"
            )

    if not file_exists(LOGGER_data_dir + os.sep + LOGGER_filename) and WRITE_LOG_data_to_file:         # test for file presence to assure a single header line
        write_header_line()

    # test if found log file header matches detected sensors
    elif WRITE_LOG_data_to_file and file_exists(LOGGER_data_dir + os.sep + LOGGER_filename):
        with open(LOGGER_data_dir + os.sep + LOGGER_filename, "r") as log_file:
            file_head_line = log_file.readline()
        #file_sens_header = SEPARATOR.join(file_head_line.split(SEPARATOR)[2:-1])
        file_sens_header = SEPARATOR.join(file_head_line.split(SEPARATOR)[2:])
        if file_sens_header.strip() != sens_header.strip() and REJECT_sensor_changes:
            raise Exception('File header not matching sensors detected')
        if file_sens_header.strip() != sens_header.strip() and not REJECT_sensor_changes:
            write_header_line()

    # ----------------- init logger ----------------------------------
    # starttime = time.time()
    # last_log_time = time.time() - LOG_every_n_seconds
    last_monotonic_log_time = time.monotonic() - LOG_every_n_seconds

    if USE_WATCHdog:
        from microcontroller import watchdog
        from watchdog import WatchDogMode
        watchdog.timeout = 7  # Set a timeout of 7 seconds
        watchdog.mode = WatchDogMode.RESET
        watchdog.feed()

    # -------------- startup message file logging --------------------------
    if WRITE_LOG_data_to_file:
        print('\nData logging to ' + LOGGER_data_dir + os.sep + LOGGER_filename + ' in progess....')
    print('Terminate with Strg+C')
    if LOG_EXCEPTIONS_to_file and (not USE_ALARM_wakeup_sleep or USE_HTTP_server): #skip on deep-sleep re-starts
        with open(LOGGER_data_dir + os.sep + LOG_EXCPTIONS_filename, "a") as except_log_file:
            try:
                except_log_file.write(f'{get_time_date_str()} (re)started\n')
            except:
                pass

    # ------------------- main loop ------------------------------------

    while True:  # if http_server is running this loop runs every second for http poll and writes data every LOG_every_n_seconds
            # without http_server running, loop runs every LOG_every_n_seconds and writes data on each run

                                                                                        # time check if http_server running
        # if time.time() - last_log_time >= LOG_every_n_seconds or not USE_HTTP_server: # no time check if http_server is not running
        if USE_WATCHdog:
            watchdog.feed()
        # re-connect wifi if connection broke
        if USE_HTTP_server and MONITOR_WIFI_connection:
            if not wifi.radio.connected:
                wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
                pool = socketpool.SocketPool(wifi.radio)
        now_monotonic_time = time.monotonic()
        if now_monotonic_time - last_monotonic_log_time >= LOG_every_n_seconds or not USE_HTTP_server:  # no time check if http_server is not running
            # last_log_time = time.time()
            last_monotonic_log_time = now_monotonic_time

            sensor_measurements = ''.join([sensor.get_measurement_str() for sensor in my_sensors])

            logline = LOGGER_name + SEPARATOR + get_time_date_str() + sensor_measurements

            if VERBOSE:
                print(logline)
            if WRITE_LOG_data_to_file:
                with open(LOGGER_data_dir + os.sep + LOGGER_filename, "a") as log_file:
                    log_file.write(logline + "\n")
                # delete the oldest 24 h of data
                if max_exception_file_size:
                    truncate_log_top(
                        LOGGER_data_dir + os.sep + LOGGER_filename,
                        MAX_log_file_size_in_bytes,
                        n_lines_to_delete=int((24 * 60 * 60) / LOG_every_n_seconds),
                    )
            if LOG_EXCEPTIONS_to_file:
                truncate_log_top(
                    LOGGER_data_dir + os.sep + LOG_EXCPTIONS_filename,
                    max_exception_file_size,
                    n_lines_to_delete=50,
                )                
            if USE_HTTP_server:
                reboot_counter_for_server -= 1  # reboot every 12 hours
                if reboot_counter_for_server <= 0 and sys.implementation.name == "circuitpython":
                    reset_microcontroller(reset_delay=3)
        # Process waiting www requests
        if USE_HTTP_server:
            try:
                pool_result = server.poll()
            except Exception as e:
                with open(LOG_EXCPTIONS_filename, "a") as except_log_filem:
                    except_log_filem.write(f"{get_time_date_str()} {e} in http server poll\n")
            if USE_ALARM_wakeup_sleep:
                # 1 second light sleep to save some power
                time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 1)
                # Do a light sleep until the alarm wakes us.
                alarm.light_sleep_until_alarms(time_alarm)
                # after light sleep code continues here
            else:
                time.sleep(1)

        else:  # alternative timing handler for none-http application
            if LOG_every_n_seconds >= ALARM_SLEEP_HOLDOFF_TIME and USE_ALARM_wakeup_sleep:
                time.sleep(ALARM_SLEEP_HOLDOFF_TIME)
                remaining_time = LOG_every_n_seconds - (ALARM_SLEEP_HOLDOFF_TIME + (time.monotonic() - last_monotonic_log_time))
                remaining_time = 0 if remaining_time <= 0 else remaining_time
                if remaining_time > 0:
                    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + remaining_time)
                    # Exit the program, and then deep sleep until the alarm wakes us. # See failure comment on top of this code
                    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
            else:
                remaining_time = LOG_every_n_seconds - (time.monotonic() - last_monotonic_log_time)
                remaining_time = 0 if remaining_time <= 0 else remaining_time
                if remaining_time > 0:
                    time.sleep(remaining_time)

    # -------------------- end main loop --------------------------


except KeyboardInterrupt:
    sys.exit('')

except Exception as e:
    if LOG_EXCEPTIONS_to_file:
        if VERBOSE:
            print(e)
        with open(LOGGER_data_dir + os.sep + LOG_EXCPTIONS_filename, "a") as except_log_file:
            try:
                except_log_file.write(get_time_date_str())
            except:
                pass
            except_log_file.write(": " + str(e) + ' ... in (main) and we will never know the line where it did happen.\n')
            # except_log_file.write(str(e)+' in line '+str(e.__traceback__.tb_lineno)+'\n') # not available in micropython
            # except_log_file.write(str(dir(e))+'\n')
            # except_log_file.write(str(dir(e.__traceback__))+'\n') # ........ no way to log the line number in micropython
                                                            # no traceback.format_exc() in micropython, this would require a re-compile! <<<<<<<<<<<<< !!!, see:
                                                            # https://github.com/micropython/micropython/issues/5110
        if str(e) == 'File header not matching sensors detected':
            raise
        if sys.implementation.name == "circuitpython":
            reset_microcontroller(reset_delay=120)  # try to get things going again
    else:
        raise  # intended for PC-applications or for debugging on microcontroller using Thonny REPL
