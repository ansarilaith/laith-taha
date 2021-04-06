#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# general imports
#-----------------------

import os
import sys
import time

# add other imports here

#-----------------------
# protect main.py
#-----------------------

# main.py is called by uPython after boot.py
# this prevents main.py from failing and
# keeps the above imports available on the REPL

import gpio_beep
import gpio_leds
from urandom import choice


beeper  = gpio_beep.BEEP(2)
blinker = gpio_leds.LED(32)
pixels  = gpio_leds.NP(4,8)

colors = ['red','deeppurple','blue','cyan','green','electricpumpkin']

try:

    while 1:

        beeper.play(gpio_beep.jingle)

        time.sleep_ms(500)

        for x in range(2):
            blinker.on()
            beeper.beep()
            blinker.off()
            time.sleep_ms(100)

        time.sleep_ms(500)

        beeper.play(gpio_beep.axelf)

        time.sleep_ms(500)

        for color in colors:
            for x in range(8):
                pixels.setp(x,color)
                time.sleep_ms(20)
                pixels.setp(x,'off')
                time.sleep_ms(10)
            for x in range(6,-1,-1):
                pixels.setp(x,color)
                time.sleep_ms(20)
                pixels.setp(x,'off')
                time.sleep_ms(10)

        time.sleep_ms(500)

        beeper.play(gpio_beep.shave)

        time.sleep(4)

except KeyboardInterrupt:
    print('Keyboard Interrupt: main.py ending.')
    
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Exception: main.py ending.')

#-----------------------
# end
#-----------------------
