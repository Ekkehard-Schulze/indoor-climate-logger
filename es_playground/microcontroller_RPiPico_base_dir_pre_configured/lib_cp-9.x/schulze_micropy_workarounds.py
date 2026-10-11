''' Fixes for functions not implemented in Micropython
   
   by es
'''
import os


def zfl(s, width):
    # Pads the provided string with leading 0's to suit the specified 'chrs' length
    # Force # characters, fill with leading 0's
    return '{:0>{w}}'.format(s, w=width)



def file_exists(fnamel): # workaround: from os.path import exists # not available in circuit/micro python
    exists = False
    try:
        f = open(fnamel, "r")
        exists = True
    except OSError:  # open failed
        exists = False
    return exists



def dir_exists(dirnamel): # workaround: from os.path import exists # not available in circuit/micro python
    exists = True
    old_dir = os.getcwd()
    try:
        os.chdir(dirnamel)
    except OSError:  # chdir failed
        exists = False
    finally:
        os.chdir(old_dir)
    return exists