''' CPython code. Intended to be run from the PC's CPython interpreter'''

import os
import shutil
import time

p_name = 'indoor-climate-logger.py'

err = False

try:
    os.rename('boot.bak', 'boot.py')
    print('\nboot.bak renamed to boot.py\n')
except Exception as e:
    print('\nno boot.bak found\n')
    err = True


try:
    if (os.path.isdir('lib_cp-8.x') or os.path.isdir('lib_cp-9.x')) and os.path.isdir('lib'):
        shutil.rmtree('lib', ignore_errors=True)
        print(r'Deleted \lib')
except Exception as e:
    pass


try:
    os.rename('lib_cp-8.x', 'lib')
    print('\\lib_cp-8.x renamed to lib\n')
except Exception as e:
    pass


try:
    os.rename('lib_cp-9.x', 'lib')
    print('\\lib_cp-9.x renamed to lib\n')
except Exception as e:
    pass

try:
    shutil.copy(p_name, 'code.py')
    print(p_name+' copied to code.py')
    x = input(f"\nDelete {p_name} ?\nEnter 'yes' to delete.\n")
    if x == 'yes':
        os.remove(p_name)
except Exception as e:
    print(f'\nno {p_name} found to be deleted\n')
    err = True
if err:
    time.sleep(3.5)
else:
    time.sleep(1.5)


# ---------------- added for hard rest---------------------------------------------------

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
import microcontroller
microcontroller.reset()
'''.splitlines()[1:]


if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    picoSerialPort = picoPorts[0].device
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
        time.sleep(0.25)
        s.write(b'\x04')   # exit raw REPL and run injected code
        time.sleep(0.25)   # give it time to run (observe the LED pulse)

        s.write(b'\x02')   # switch to normal REPL mode
        time.sleep(0.5)    # give it time to complete
        s.write(b'\x04')   # execute a 'soft reset' and trigger 'main.py'

    print( '\nRaspberry Pi Pico found at '+str(picoSerialPort)+'\n' )
    print('\nboot.bak renamed to boot.py and controller reset\n')
    time.sleep(1.5)
