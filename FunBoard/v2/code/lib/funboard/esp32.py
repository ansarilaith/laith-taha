#-----------------------
# imports
#-----------------------

import os
import gc
from esp32 import raw_temperature
from esp32 import hall_sensor

#-----------------------
# funboard variables class
#-----------------------

class ESP32:

    def __init__(self,reset_pin):
        self.reset_pin = reset_pin

    @property
    def reset(self):
        print('HARDWARE RESET')
        import time
        from machine import Pin
        time.sleep_ms(100)
        if self.reset_pin:
            Pin(self.reset_pin,Pin.OUT,value=0)
        return False

    @property
    def temp(self):
        return round((raw_temperature()-32)/1.8,1)

    @property
    def tempf(self):
        return raw_temperature()

    @property
    def hall(self):
        try:
            return hall_sensor()
        except:
            return 0

    @property
    def memory(self):
        gc.collect()
        free = gc.mem_free()
        used = gc.mem_alloc()
        return {'free':free,
                'used':used,
                'total':free+used,
                'perc':round(100*used/(free+used),2)}

    @property
    def flash(self):
        bsize,frsize,blocks,bfree,bavail,files,ffree,favail,flag,namemax = os.statvfs('/')
        size = bsize * blocks
        free = bsize * bfree
        return {'free':free,
                'used':size-free,
                'total':size,
                'perc':round(100*(size-free)/size,2)}

#-----------------------
# end
#-----------------------
