#-----------------------
# notify
#-----------------------

print('LOAD: sdcard.py')

#-----------------------
# imports
#-----------------------

import os
import sys
import time

from machine import Pin
from machine import SDCard

#-----------------------
# SLOT 2 class
#-----------------------

class SLOT2:

    target = '/sd'

    mount_point = None # mount point
    mounted = False # True on mount success
    sdcard = None # SDCard object
    freq = 10000000
    
    slot =  2
    sck  = 18 # default slot 2
    cs   =  5 # default slot 2, but could be None
    miso = 19 # default slot 2
    mosi = 23 # default slot 2

    def mount(self,show_error=False):
        try:
            self.sdcard = self._make()
            print('SDCard SPI Init')
            os.mount(self.sdcard,
                     self.target)
            self.mount_point = self.target
            self.mounted = True
            time.sleep_ms(100)
            print('SDCard mount at',self.mount_point)
            return True
        except Exception as e:
            if show_error:
                sys.print_exception(e)
            print('SDCard Mount Error')
            try:
                self.unmount()
            except:
                pass
            return False

    def unmount(self,show_error=False):
        success = True
        try:
            os.umount(self.mount_point)
            self.mounted = False
            print('SDCard Unmounted')
        except Exception as e:
            success = False
            if show_error:
                sys.print_exception(e)
                print('SDCard Unmount Error')
        try:
            self.sdcard.deinit()
            self.sdcard = None
            print('SDCard SPI deinit.')
        except Exception as e:
            success = False
            if show_error:
                sys.print_exception(e)
                print('SDCard SPI deinit Error.')
        return success

    def format(self,cs=None,warn=True,show_error=False):
        if warn:
            print()
            print('WARNING: This will DESTROY ALL DATA on the SDCard!!!')
            print()
            print('Are you sure you want to continue?',end=' ')
            if (input('> ').strip()+'n')[0].lower() != 'y':
                return False
        try:
            self.unmount()
            sdcard = self._make()
            os.VfsFat.mkfs(sdcard)
            sdcard.deinit()
            print('SDCard Fat32 Formated')
            return True
        except Exception as e:
            if show_error:
                sys.print_exception(e)            
            print('SDCard Format Error')
            return False

    def _make(self):
        return SDCard(slot=self.slot,miso=self.miso,mosi=self.mosi,sck=self.sck,cs=self.cs,freq=self.freq)

#-----------------------
# SLOT 3 class
#-----------------------

class SLOT3(SLOT2):

    slot =  3 
    sck  = 14 # default slot 3
    cs   = 15 # default slot 3
    miso = 12 # default slot 3
    mosi = 13 # default slot 3

#-----------------------
# end
#-----------------------
