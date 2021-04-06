#-----------------------
# imports
#-----------------------

import sys,time
from machine import Pin
from neopixel import NeoPixel

#-----------------------
# plain LEDs 
#-----------------------

# class wrapper
# keeps pin as input when off

class LED:

    # pin values
    pin = None # gpio number
    anode = True # led anode is connected to gpio

    # blink values
    ontime = 50
    offtime = 250

    def __init__(self,pin,anode=True,initon=False):

        self.pin = abs(int(pin))

        if not anode:
            self.anode = False

        if initon:
            self.on()

    def on(self):

        if self.pin is not None:

            if self.anode:
                Pin(self.pin,Pin.OUT,value=1)

            else:
                Pin(self.pin,Pin.OUT,value=0)

    def off(self):

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

#-----------------------
# micro pixel class
#-----------------------

class PIXELS:

    # brightness out of 255
    brightness = 32

    # name: color tuples
    # bold colors
    colors = {
        'blue': (0, 0, 255),
        'deepbluegatoraide': (0, 32, 255),
        'bluegatoraide': (0, 127, 255),
        'cyan': (0, 255, 255),
        'aqua': (0, 255, 127),
        'electricmint': (0, 255, 32),
        'green': (0, 255, 0),
        'electriclime': (32, 255, 0),
        'greenyellow': (127, 255, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 127, 0),
        'electricpumpkin': (255, 32, 0),
        'red': (255, 0, 0),
        'deeppink': (255, 0, 32),
        'pink': (255, 0, 127),
        'magenta': (255, 0, 255),
        'purple': (127, 0, 255),
        'deeppurple': (32, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'off': (0, 0, 0),
        }

    # init
    def __init__(self,pin,pixels):

        self.pin = pin
        self.p = Pin(self.pin,Pin.OUT)

        self.pixels = pixels
        self.np = NeoPixel(self.p,self.pixels)

    # all off
    def off(self):

        for pixel in range(self.pixels):
            self.np[pixel] = (0,0,0)

        self.np.write()

    # kill
    def kill(self):

        self.off()
        Pin(self.pin,Pin.IN,Pin.PULL_UP)

    # brightness reset
    def set_brightness(self,brightness=0):

        # set
        old = self.brightness
        new = min(255,abs(brightness))
        self.brightness = new

        # redo
        scale = new/old
        for pixel in range(self.pixels):
            self.np[pixel] = tuple([int(min(255,x*scale)) for x in self.np[pixel]])
        self.np.write()

    # get a color
    def get_color(self,color,brightness=None):

        # leave color tuples as is
        if type(color) in (list,tuple):
            return tuple(list(color)+[0,0,0])[:3]

        # get text color value
        color = ''.join(str(color).split())
        value = self.colors.get(color,(255,255,255))

        # scale
        return tuple([int(x*(brightness or self.brightness)/255) for x in value])

    # set a pixel
    def setp(self,pixel,color,brightness=None,write=True):
        self.np[min(pixel,self.pixels-1)] = self.get_color(color,brightness)
        if write:
            self.np.write()

    # sweep up and back
    def sweep(self,color=None,brightness=None,ontime=25,offtime=5):
        for p in (0,1,2,3,4,5,6,7,6,5,4,3,2,1,0):
            self.setp(p,color or ['red','blue','green'][p%3],brightness)
            time.sleep_ms(ontime)
            self.setp(p,(0,0,0))
            time.sleep_ms(offtime)

#-----------------------
# end
#-----------------------
