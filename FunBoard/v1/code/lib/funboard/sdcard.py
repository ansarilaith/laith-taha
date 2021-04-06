#-----------------------
# imports
#-----------------------

import os
import time
from machine import SDCard

#-----------------------
# tools class
#-----------------------

class SDCARD:

    mount_point = '/sd' # target mount point
    
    _sdcard = None # SDCard object
    _mount_point = None # current mount point
    slot =  3 # default slot 3
    cs   = 15 # default slot 3
    sck  = 14 # default slot 3
    mosi = 13 # default slot 3
    miso = 12 # default slot 3

    def __init__(self,slot=None,cs=None,sck=None,mosi=None,miso=None):
        self.slot = slot or self.slot
        self.cs = cs or self.cs
        self.sck = sck or self.sck
        self.mosi = mosi or self.mosi
        self.miso = miso or self.miso
        #print('SD SPI on INIT:',self.slot,self.cs,self.sck,self.mosi,self.miso)

    def error(self,e=None,s='SDCard not mounted.',unmount=False):

        if e:
            pass
            #from sys import print_exception
            #print_exception(e)
            #del print_exception

        if s:
            print('ERROR:',s)

        if unmount:
            print('SDCard MAJOR ERROR! Unmounting.')
            self.unmount(show=True)

    def sdpath(self,path=None):

        if not (self._sdcard and self._mount_point):
            self.error()
            return None

        path = path or ''
        path = [x.replace(' ','') for x in path.split('/') if x.replace(' ','')]

        if path:
            return self._mount_point + '/' + '/'.join(path)

        return self._mount_point

    def mount(self):

        self.unmount(show=False)

        try:
            #print('SD SPI on MOUNT:',self.slot,self.cs,self.sck,self.mosi,self.miso)
            self._sdcard = SDCard(slot=self.slot,cs=self.cs,sck=self.sck,mosi=self.mosi,miso=self.miso)
            self.mount_point = self.mount_point.replace(' ','').rstrip('/')
            self.mount_point = self.mount_point or '/sd'
            os.mount(self._sdcard,self.mount_point)
            self._mount_point = self.mount_point
            time.sleep_ms(100)
            print('SDCard mount at',self._mount_point)
            return True

        except Exception as e:
            self.error(e,'SDCard mount failed.')
            self.unmount(show=False)
            return False

    def unmount(self,show=True):

        try:
            os.umount(self._mount_point)
            self._mount_point = None

            self._sdcard.deinit()
            self._sdcard = None

            if show:
                print('SDCard unmounted.')
            return True

        except Exception as e:
            if show:
                self.error(e,'SDCard stage 1 unmount failed.')
        
            try:
                self._sdcard.deinit()

                if show:
                    print('SDCard stage 2 deinit success.')

            except Exception as e:
                if show:
                    self.error(e,'SDCard stage 2 deinit failed.')

        self._mount_point = None
        self._sdcard = None

        return False

    def format(self,warn=True):

        if warn:
            print()
            print('WARNING: This will DESTROY ALL DATA on the SDCard!!!')
            print()
            print('Are you sure you want to continue?',end=' ')
            if (input('> ').strip()+'n')[0].lower() != 'y':
                return False

        try:

            self.unmount(show=False)

            _sdcard = SDCard(slot=self.slot,cs=self.cs,sck=self.sck,mosi=self.mosi,miso=self.miso)
            os.VfsFat.mkfs(_sdcard)
            _sdcard.deinit()
            print('SDCard Fat32 format complete.')

            self.mount()
            with open(self.sdpath('FAT32_FORMATED'),'w') as f:
                try:
                    f.write(rtc.dtstamp()+'\n')
                except:
                    f.write(str(time.time())+'\n')
                f.close()
            print('SDCard initial write success.')

            return True

        except Exception as e:
            self.error(e,'SDCard format failed.')

#-----------------------
# end
#-----------------------
