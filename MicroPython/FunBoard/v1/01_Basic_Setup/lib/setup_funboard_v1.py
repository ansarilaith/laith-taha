#-----------------------
# notify
#-----------------------

print('RUN: setup_funboard_v1.py')

#-----------------------
# define board constants
#-----------------------

from micropython import const

PIN_MANRST    = const(15) # RESET
PIN_LED       = const(32) # Blue LED
PIN_PIXELS    = const( 4) # 8 Micro Pixels
PIN_BUZZER    = const( 2) # Buzzer
PIN_PROG      = const( 0) # PROG Button
PIN_SD_CS     = const(27) # SDCard non-standard
PIN_SD_SCL    = const(14) # SDCard Slot 1
PIN_SD_MOSI   = const(13) # SDCard Slot 1
PIN_SD_MISO   = const(12) # SDCard Slot 1
PIN_UART1_TX  = const(17) # UART
PIN_UART1_RX  = const(16) # UART
PIN_SPI2_CS   = const( 5) # SPI-2
PIN_SPI2_SCL  = const(18) # SPI-2
PIN_SPI2_MISO = const(19) # SPI-2
PIN_SPI2_MOSI = const(23) # SPI-2
PIN_I2C1_DATA = const(26) # I2C-1
PIN_I2C1_CLK  = const(25) # I2C-1


BOARD_NAME = 'FUNBOARD-V1'
BOARD_DATE = '2021-01-06'

print('BOARD SETUP: {} {}'.format(BOARD_NAME,BOARD_DATE))

#-----------------------
# immediate UI feedback
#-----------------------

# turn on blue led (led1)

from machine import Pin
Pin(PIN_LED,Pin.OUT,value=1)

#-----------------------
# esp32 object 
#-----------------------

import os
import gc
from esp32 import raw_temperature
from esp32 import hall_sensor

class ESP32:

    @property
    def reset(self):
        print('HARDWARE RESET')
        time.sleep_ms(100)
        if PIN_MANRST:
            Pin(PIN_MANRST,Pin.OUT,value=0)
        return False

    @property
    def temp(self):
        return raw_temperature()

    @property
    def tempf(self):
        return raw_temperature()*1.8 + 32

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
    
esp32 = ESP32()

#-----------------------
# hardware reset
#-----------------------

from machine import reset_cause
reset_cause = reset_cause()
print('LAST RESET:',{
    # machine.PWRON_RESET     = 1
    # machine.HARD_RESET      = 2
    # machine.WDT_RESET       = 3
    # machine.DEEPSLEEP_RESET = 4
    # machine.SOFT_RESET      = 5
    1: 'POWERON',
    2: 'HARDWARE',
    3: 'WATCHDOG',
    4: 'DEEPSLEEP',
    5: 'SOFTWARE'}.get(reset_cause,'UNKNOWN'))

# software resets DO NOT clear peripherals
# machine.reset() and WDT don't do full resets either
if reset_cause >= 3:
    esp32.reset

#-----------------------
# UI feedback objects
#-----------------------

from gpio_beep import BEEP
beeper = BEEP(PIN_BUZZER)
beeper.jingle(vol=20) # I'm awake!

from gpio_leds import LED
led = LED(PIN_LED)



#-----------------------
# additional imports
#-----------------------

import os
import sys
import time
import gc

import device_sdcard 

# garbage collect post import
gc.collect()

#-----------------------
# sdcard SPI bus 1 
#-----------------------

sdcard = device_sdcard.SDCARD(slot=3,
                              cs=PIN_SD_CS,
                              sck=PIN_SD_SCL,
                              mosi=PIN_SD_MOSI,
                              miso=PIN_SD_MISO)
sdcard.mount()

#-----------------------
# ready 
#-----------------------

# final garbage collect
gc.collect()

# let user know
print('BOARD IS READY')
beeper.jingle2()
led.off()

#-----------------------
# end
#-----------------------
