#!/usr/bin/env python3
'''CPython code. This works only if microcontroller is not asleep.
Otherwise inject command using Thonny
Intended to be run from the PC's CPython interpreter'''
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
# see section 4.8 RTC of https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf and in particular section 4.8.6 
# for the RTC_BASE address (0x4005C000) and details of the RD2040 setup registers used to program the RT (also read
# 2.1.2. on Atomic Register Access)
#
# https://github.com/thonny/thonny/issues/1592

# Attention: the time delays are critical!

from serial.tools import list_ports
import serial, time

picoPorts_a = list(list_ports.grep("2E8A:0005"))
picoPorts_b = list(list_ports.grep("239A:80F4"))
picoWPorts = list(list_ports.grep("239A:8120"))
pico2WPorts = list(list_ports.grep("239A:8162"))

picoPorts = picoPorts_a + picoPorts_b + picoWPorts + pico2WPorts


utcTime = str( int(time.time()) )


pythonInject = r'''
import os
os.rename("/boot.py", "/boot.bak")
'''.splitlines()[1:]


if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    picoSerialPort = picoPorts[0].device
    print( '\nRaspberry Pi Pico found at '+str(picoSerialPort)+'...\n' )    
    with serial.Serial(picoSerialPort) as s:
        s.write(b'\x03')   # interrupt the currently running code
        time.sleep(1.3)        
        s.write(b'\x03')   # (do it twice to be certain)
        time.sleep(1.3)                
        s.write(b'\x01')   # switch to raw REPL mode & inject code
        time.sleep(0.7)         
        for code in pythonInject:
            s.write(bytes(code+'\r\n', 'ascii'))
            time.sleep(0.05)
        time.sleep(0.3)
        s.write(b'\x04')   # exit raw REPL and run injected code
        time.sleep(0.3)   # give it time to run (observe the LED pulse)

        s.write(b'\x02')   # switch to normal REPL mode
        time.sleep(0.5)    # give it time to complete
        s.write(b'\x04')   # execute a 'soft reset' and trigger 'main.py'


    print('\nboot.py renamed to boot.bak\n')
    print('\nReset device manually to reboot.\n')    
    time.sleep(3.0)
