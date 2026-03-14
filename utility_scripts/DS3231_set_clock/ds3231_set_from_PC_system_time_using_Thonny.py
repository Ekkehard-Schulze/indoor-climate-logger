'''DS3231 set on microcontroller. Use Thonny IDE to 
   tranfer PC-system time on startup to the controller.
   Then set DS3231 with optional offset_hours using the controller's local time.

   Attention: offset does not handle hour overflows, and fails repectively in these border cases.
   This quick and dirty approach was done, because micropython has not
   datetime module providing timedelta. Could have tried Adafruit_datetime in CircuitPython instead.
   '''

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of reading and writing the time for the DS3231 real-time clock.
# Change the if False to if True below to set the time, otherwise it will just
# print the current date and time every second.  Notice also comments to adjust
# for working with hardware vs. software I2C.

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
import board
import busio
import adafruit_ds3231

HOURS_OFFSET = +0  # <<<<<<<<<<<<<<<<<<<<<<<<<<< user setting

DO_SET_TIME = True


# Lookup table for names of days (nicer printing).
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def get_i2c_bus(bus_clock = 100000):
    ''' get i2c from board specific context. Inteded for es lib usage from i2c_scan_switch_boards.py'''
    
    raspberry_pi_pico_version_names = [
        "raspberry_pi_pico",
        "raspberry_pi_pico2",
        "raspberry_pi_pico_w",
        "raspberry_pi_pico2_w",
    ]    

    if board.board_id in raspberry_pi_pico_version_names:
        i2cl = busio.I2C(board.GP5, board.GP4, frequency=bus_clock) # Circuit py default is 400000

    else:
        i2cl = busio.I2C(board.SCL, board.SDA, frequency=bus_clock) # Circuit py default is 400000

    return i2cl



i2c = get_i2c_bus()  

rtc = adafruit_ds3231.DS3231(i2c)


# pylint: disable-msg=using-constant-test
if DO_SET_TIME:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    now =  time.localtime()

    t =  time.struct_time(
        (
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            now.tm_hour + HOURS_OFFSET,  # Attention: this does not handle overflows, and fails in border cases
            now.tm_min,
            now.tm_sec,
            now.tm_wday,
            now.tm_yday,
            -1,
        )
                )
    
    # t = time.struct_time((2025, 12, 31, 20, 53, 00, 0,-3, 365, 0))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t
    print()
# pylint: enable-msg=using-constant-test

# Main loop:
while True:
    t = rtc.datetime
    # print(t)     # uncomment for debugging
    print(
        "The date is {} {}/{}/{}".format(
            DAYS[int(t.tm_wday)], t.tm_mday, t.tm_mon, t.tm_year
        )
    )
    print("The time is {}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
    time.sleep(1)  # wait a second
