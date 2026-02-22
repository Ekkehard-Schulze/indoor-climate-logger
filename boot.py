# this goes to boot.py
# remount of the USB-File system if  Blackpill button is pressed during reset for r/w access, USB read only
# Attention: files written by the microcontroller are invsible from the USB-side before the next reset,
#            they become visible after the next reset
# --------------------
# Attention: REPL kann remove the boot.py from the USB-read only locked file system:
# import os; os.rename("/boot.py", "/boot.bak")

import board
import storage

storage.remount(mount_path="/", readonly=False)
