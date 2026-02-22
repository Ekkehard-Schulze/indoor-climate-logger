#!/usr/bin/python3
'''
downloads data from picoW logger for archive.
picoW logger has a rolling buffer and overwrites itself 
when memory is full. This script is used to save and to
archive data to prevent data loss.

# pico_logger MHZ19 crontab entry for Saturday morning download
# Min hour day month weekday,  (year is NOT available)
# --- ---  --- ----- -------
51 00 * * 6  /home/es/logged_data/pico_logger/logger_www_poll.pyw   >/dev/null 2>>/dev/null

followed by merge_sort_normalize_clean.py

Attention: download once a week lost data for RaspberryPi PicoW, recommend
# every third day
59 23 */3 * * /home/es/logged_data/pico_logger/logger_www_poll.pyw   >/dev/null 2>>/dev/null

'''

import os
import sys
from datetime import datetime
from urllib.request import urlopen


url = "http://192.168.178.42//MHZ_19_CO2_log.tsv"

page = urlopen(url)
html_bytes = page.read()
html_or_txt = html_bytes.decode("utf-8")  # string multiline


# crontab run has ~/ as working directory and would consequently save to ~/
# the following line ensures that the output file goes besides the script
filename = os.path.dirname(sys.argv[0])+os.sep+datetime.now().strftime("%Y%m%d_%H%M%S")+"_MHZ_19_CO2_log.tsv"

with open( filename, 'w', encoding='utf-8', errors="ignore") as f:
    f.write(html_or_txt)
