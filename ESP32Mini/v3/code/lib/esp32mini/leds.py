#-----------------------
# imports
#-----------------------

import sys,time
from machine import Pin, PWM

#-----------------------
# plain LEDs 
#-----------------------

# class wrapper
# keeps pin as input when off

class LED:

    # pin values
    pin = None # gpio number

    # blink values
    ontime = 50
    offtime = 250

    # pwm values
    # freq can be from 1Hz to 40mHz
    # duty cycle can be from 1-1023
    pwmo = None # pwm object
    pwmd = 1023 # last duty cycle
    pwmf = 1000 # freq in Hz

    def __init__(self,pin,initon=False):

        self.pin = abs(int(pin))

        self.pwmx(force=True)

        if initon:
            self.on()

        else:
            self.off()

    def on(self):

        self.pwmx()

        if self.pin is not None:
            Pin(self.pin,Pin.OUT,value=1)

    def off(self):

        self.pwmx()

        if self.pin is not None:
            Pin(self.pin,Pin.IN,pull=None)

    def blink(self,count=1,ontime=None,offtime=None):

        if not ontime:
            ontime = self.ontime

        if not offtime:
            offtime = self.offtime

        for x in range(count):

            self.on()
            time.sleep_ms(ontime)

            self.off()
            time.sleep_ms(offtime)

    def pwmx(self,force=False):

        if force:
            try:
                PWM(Pin(self.pin)).deinit()
                self.pwmo = None
            except:
                pass

        elif self.pwmo:
            try:
                self.pwmo.deinit()
                self.pwmo = None
            except:
                pass

    def pwm(self,percent=100):

        self.pwmd = int( 1023 * min(100,abs(percent)) / 100 )

        if self.pwmo:
            self.pwmo.duty(self.pwmd)

        else:
            self.pwmo = PWM(Pin(self.pin,Pin.OUT,value=0),freq=self.pwmf,duty=self.pwmd)

    def pwm2(self,start=0,end=100,pause=10):

        if start > end:
            for x in range(start,end-1,-1):
                self.pwm(x)
                time.sleep_ms(pause)

        elif start < end:
            for x in range(start,end+1,1):
                self.pwm(x)
                time.sleep_ms(pause)

        else:
            self.pwm(start)     

#-----------------------
# end
#-----------------------
