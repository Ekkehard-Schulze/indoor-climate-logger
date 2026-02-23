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
