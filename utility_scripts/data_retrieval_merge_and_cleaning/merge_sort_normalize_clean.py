#!/usr/bin/env python3
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

''' merge time-log files, sort line-wise, remove duplicated lines, put logger header at top, delete comment lines

usage: merge_sort_normalize.py *.txt

aim: merge a collection of log files from a device with limited memory to a single larger
     file representing a longer time intervall than the device could originally store.
     Usd for logs from RaspberryPiPicoW

removes lines with incorrectly formatted datetimes

# pico_logger MHZ19 crontab entry for Saturday morning download
51 00 * * 6  /home/es/logged_data/pico_logger/logger_www_poll.pyw   >/dev/null 2>>/dev/null
53 00 * * 6  cd /home/es/logged_data/pico_logger;/home/es/logged_data/pico_logger/merge_sort_normalize_clean.pyw   >/dev/null 2>>/dev/null
'''

import glob
import sys
import os
import re

default_parameter = '*.tsv'

outfile_extension = '.tsv'

outfile_suffix = '_merged'

COMMENT_char = "#"

delete_older_merge_files = True

header_line_signature = 'logger-id'

date_pattern1 = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d')
date_pattern2 = re.compile(r'\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d')
input_lines = []

date_tag = re.compile('^[_01234567890]+')


def qualify_line(ll):
    ''' test is logger line is valid, a) header b) comment c) data line with correctly iso-formatted datetime'''
    if ll.startswith(header_line_signature) or ll.startswith('#'):
        return True
    if re.search(date_pattern1, ll):
        return True
    if re.search(date_pattern2, ll):
        return True        
    return False
       

def store_latest_file_name(fname_new, fname_stored=['000']): 
    '''Stores latest filename of names like 20241012_005106_MHZ_19_CO2_log.
    Before I used the last arg found, this was for MS_Windows 
    the latest file whereas unix used the earliest name
    This is a function, which stores a state.
    see also:
    https://www.vaia.com/en-us/textbooks/computer-science/learning-python-5-edition/chapter-17/problem-7-name-three-or-more-ways-to-retain-state-informatio/
    
    https://stackoverflow.com/questions/11866419/how-to-maintain-state-in-python-without-classes
    
    '''
    old_date = int(re.findall(date_tag, fname_stored[0])[0].replace('_',''))
    new_date = int(re.findall(date_tag, fname_new)[0].replace('_',''))
    if new_date > old_date:
        fname_stored[0] = fname_new
    return fname_stored[0]

    
# ------------- main ------------------------------    

if len(sys.argv) >= 2:
    for parg in sys.argv[1:]:         # required for wildcards on unix, because they arrive here already expanded by bash
        for arg in glob.glob(parg):   # required for wildcards on windows 
            store_latest_file_name(arg)
            with open(arg, "r") as infile:
                input_lines+= infile.readlines()

else:                                          # use defaults, because no command line parameters were passed
    for arg in glob.glob(default_parameter):   # required for wildcards on windows
        store_latest_file_name(arg)
        with open(arg, "r", encoding='utf-8-sig', errors="ignore") as infile:
            input_lines+= infile.readlines()

input_lines = [line for line in input_lines if not line.startswith(COMMENT_char)] 

input_lines.sort()

# eliminate duplicated lines. This is data lines and header lines
# a single header line remains at the bottom
previous = ''
r_input_lines = []
for l in input_lines:
    if l != previous and qualify_line(l):   
        r_input_lines.append(l)
        previous = l 

# move single header line from bottom to top
if r_input_lines[-1].startswith(header_line_signature):
    r_input_lines = [r_input_lines[-1]]+r_input_lines[:-1] 

outfile_name = os.path.splitext(store_latest_file_name('000'))[0]+outfile_suffix +outfile_extension

with open(outfile_name, "w") as outfile:
    outfile.writelines(r_input_lines)

if delete_older_merge_files:
    [os.remove(f) for f in glob.glob("*"+outfile_suffix+outfile_extension) if f != outfile_name]
