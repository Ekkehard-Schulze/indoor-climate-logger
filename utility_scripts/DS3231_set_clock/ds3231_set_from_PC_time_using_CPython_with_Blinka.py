#!/usr/bin/env python3
''' set DS3231 from PC's system time to UTC ± offset_hours using the Adafruit Blinka library.

    Runs on PC's or RPi's CPython with Blinka library.
    
    UTC-offset ours comes from a command-line parameter,
 
    Requires an USB-I2C hardware, either  RPiPico with U2IF frimware, or FT232H, or MCP2221,  
    or, alternatively, RasperryPi with native I2C.

    Provides board independent procedure to get i2c bus for 
    if using Adafruit-Blinka-USB-ICs you may import board only after 
    'set_i2c_environment_vars_for_Blinka' 
    __main__ scans i2c bus
'''
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


import time
import os
import sys
import platform
import argparse
from datetime import timedelta, datetime, timezone

DO_SET_TIME = True

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

    # import platform 
    if platform.system() == 'Windows':       
        for blinka_ic in USB_IC_selector_for_Blinka[mode]:  
            os.environ[ blinka_ic[0]] =  blinka_ic[1] # put IC-specifying env var in py code instead of administrating the environment in windows 
        if ("BLINKA_FT232H", "1") in USB_IC_selector_for_Blinka[mode]: # if FT232H IC is selected reject FTDI driver, we need libusbK
            if Win_FT232H_with_ftdi_driver_present():
                sys.exit('\nno libusbK driver for FT232H present. Use Zadig first.\n')
    elif platform.system() == 'Linux':
        for blinka_ic in USB_IC_selector_for_Blinka[mode]:  
            os.environ[ blinka_ic[0]] =  blinka_ic[1] # put IC-specifying env var in py code instead of administrating the 
    elif platform.system() == 'Darwin': # macOS
        for blinka_ic in USB_IC_selector_for_Blinka[mode]:  
            os.environ[ blinka_ic[0]] =  blinka_ic[1] # put IC-specifying env var in py code instead of administrating the 




def get_i2c_bus(bus_clock = 100000):
    ''' get i2c from board specific context. Inteded for es lib usage from i2c_scan_switch_boards.py'''
    import board
    import busio
    
    raspberry_pi_pico_version_names = [
        "raspberry_pi_pico",
        "raspberry_pi_pico2",
        "raspberry_pi_pico_w",
        "raspberry_pi_pico2_w",
    ]    

    if board.board_id in raspberry_pi_pico_version_names:
        i2cl = busio.I2C(board.GP5, board.GP4, frequency=bus_clock) # Circuit py default is 400000

    elif board.board_id == "PICO_U2IF":
        i2cl = busio.I2C(board.SCL0, board.SDA0, frequency=bus_clock) # Circuit py default is 400000
        #i2cl = busio.I2C(board.SCL1, board.SDA1, frequency=bus_clock) # Circuit py default is 400000
        #i2cl = busio.I2C(board.SCL, board.SDA, frequency=bus_clock) # defaults to SCL0, SDA0

    else:
        i2cl = busio.I2C(board.SCL, board.SDA, frequency=bus_clock) # Circuit py default is 400000

    return i2cl



def i2cscan(i2cl):
    '''Print i2cscan until Cont-C pressed'''
    while not i2cl.try_lock():
        pass
    try:
        while True:
            print("--------------------------------------------------")
            print("Responding I2C addresses: ",end = '')
            print([hex(x) for x in i2cl.scan()])
            print("--------------------------------------------------")
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    i2cl.unlock()






if __name__ == "__main__":

    if sys.implementation.name == "cpython": 
        #import platform
        import adafruit_ds3231        
        parser = argparse.ArgumentParser( \
                description="Ekkehard's DS3231 setter for Blinka",
                epilog="Have fun with microcontrollers", formatter_class=argparse.RawTextHelpFormatter)  # init object

        # ---------- define arguments
        parser.add_argument('-u', '--USB_IC', default="0", help='0:RPi 1: FT232H  2: MCP2221  3: Pico U2IF') # string
        parser.add_argument('-o', '--UTC_offset_hours', default="0", help='0:RPi 1: FT232H  2: MCP2221  3: Pico U2IF') # string 
        parser.add_argument('-s', '--scan_i2c',  default=False, help="scan i2c bus", action="store_true")

        # --------------  collect arguments
        args = parser.parse_args()    
        # ------- poke arguments
        if args.USB_IC == "0" and not platform.system() == 'Linux' and not "ARM" in platform.machine().upper():
            parser.print_help()
            sys.exit("You have to choose an USB-Ic.")    
        if not args.USB_IC in '0123':
            sys.exit('-u argument must either be 0, 1, 2, or 3\n')
        set_i2c_environment_vars_for_Blinka(int(args.USB_IC))


        i2c = get_i2c_bus()
        
        if args.scan_i2c:
            i2cscan(i2c)

        d = datetime.now(timezone.utc) + timedelta(hours=int(args.UTC_offset_hours)) # only datetime module has timedelta
        t = time.struct_time((d.year, d.month, d.day, d.hour, d.minute, d.second, 0, d.weekday(), 0,   -1))


        rtc = adafruit_ds3231.DS3231(i2c)

        # Lookup table for names of days (nicer printing).
        days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


        # pylint: disable-msg=using-constant-test
        if DO_SET_TIME:  # change to True if you want to set the time!
            #                     year, mon, date, hour, min, sec, wday, yday, isdst
            # t = time.struct_time((2025, 12, 31, 20, 53, 00, 0,-3, 365, 0))
            # you must set year, mon, date, hour, min, sec and weekday
            # yearday is not supported, isdst can be set but we don't do anything with it at this time
            print("Setting time to:", t)  # uncomment for debugging
            rtc.datetime = t
            print()
        # pylint: enable-msg=using-constant-test

        # Main loop: show time
        while True:
            t = rtc.datetime
            # print(t)     # uncomment for debugging
            print(
                "The date is {} {}/{}/{}".format(
                    days[int(t.tm_wday)], t.tm_mday, t.tm_mon, t.tm_year
                )
            )
            print("The time is {}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
            time.sleep(1)  # wait a second







    elif sys.implementation.name == "circuitpython":
        time.sleep(1.5) # may be required for Pico battery power

    i2cscan(get_i2c_bus())
