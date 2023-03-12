#-----------------------
# notify
#-----------------------

# Stolen from Clayton Darwin

print('LOAD: pixels.py')

#-----------------------
# imports
#-----------------------

import sys,time
from machine import Pin
from neopixel import NeoPixel

#-----------------------
# neopixel class
#-----------------------

class PIXELS:

    # default pixel pin
    pin = 32

    # brightness out of 255
    brightness = 32

    # neopixel objects
    p   = None # pin object
    np  = None # neopixel object
    npc = None # neopixel count

    # name: color tuples
    # bold colors
    cvalues = {
        'red':    (255,  0,  0),
        'orange': (255, 16,  0),
        'sun':    (255, 64,  0),
        'yellow': (255,160,  0),
        'lime':   ( 64,255,  0),
        'green':  (  0,255,  0),
        'mint':   (  0,255, 16),
        'cyan':   (  0,255, 96),
        'sky':    (  0,255,255),
        'blue':   (  0,  0,255),
        'purple': (128, 0, 255),
        'magenta':(255, 0, 255),
        'pink':   (255, 0, 128),
        'white':  (255,255,192),
        'black':  (  0,  0,  0),
        'off':    (  0,  0,  0),
        }

    # display colors
    def colors(self,return_colors=False):
        cl = list(self.cvalues.items())
        cl.sort()
        if return_colors:
            return [x[0] for x in cl]
        print('Pixel Colors:')
        for c,v in cl:
            print('  {:<7}: {}'.format(c,v))

    # init
    def __init__(self,pin=None,pixels=1):
        if pin != None:
            self.pin = pin
        self.npc = pixels
        self.p = Pin(self.pin,Pin.OUT)
        self.np = NeoPixel(self.p,pixels)

    # off (save pixel color)
    def off(self,write=True):
        try:
            for x in range(self.npc):
                self.np[x] = (0,0,0)
            self.np.write()
        except:
            pass

    # kill
    def kill(self):
        self.off()
        try:
            Pin(self.pin,Pin.IN,Pin.PULL_UP)
        except:
            pass
        finally:
            self.p = None
            self.np = None
            self.npc = None

    # brightness reset
    def set_brightness(self,brightness=0):
        self.brightness = min(255,abs(brightness))

    # make/select a color
    def make_color(self,color,brightness=None):
        if type(color) in (list,tuple):
            return tuple(list(color)+[0,0,0])[:3]
        if brightness == 0:
            return (0,0,0)
        v = self.cvalues.get(color,(255,0,0))
        b = brightness or self.brightness
        return tuple([int(x*b/255) for x in v])

    # set pixel
    def setp(self,pixel=0,color=None,brightness=None,write=False):
        if color:
            self.np[pixel] = self.make_color(color,brightness)
        if write:
            self.np.write()

    # write
    def write(self):
        self.np.write()

    # blink
    def blink(self,pixel=0,color='red',count=1,brightness=None,ontime=25,offtime=75):
        for x in range(max(count,1)):
            self.setp(pixel,color,brightness,True)
            time.sleep_ms(ontime)
            self.off()
            time.sleep_ms(offtime)

    # run (test pattern)
    def run(self,color='red',brightness=None,ontime=10,offtime=1):
        self.off()
        color = self.make_color(color)
        kbi = False
        try:
            for x in range(self.npc):
                self.setp(x,color,brightness,True)
                time.sleep_ms(ontime)
                self.setp(x,(0,0,0),None,True)
                time.sleep_ms(offtime)
            self.off()
            return
        except Exception as e:
            self.off()
            raise e

    # random pixel blink
    def rblink(self,colors=[],pixels=1,times=0,brightness=None,ontime=10,offtime=10):
        from random import randint,choice
        stop = self.npc-1
        if not colors:
            colors = [color for color in self.cvalues.keys() if color not in ('black','off')]
        colors = [self.make_color(color,brightness) for color in colors]
        try:
            while 1:
                used = []
                while len(used) < pixels:
                    pixel = randint(0,stop)
                    if pixel not in used:
                        used.append(pixel)
                        color = choice(colors)
                        self.np[pixel] = color
                self.np.write()
                time.sleep_ms(ontime)
                for pixel in used:
                    self.np[pixel] = (0,0,0)
                self.np.write()
                time.sleep_ms(offtime)
                if times:
                    times -= 1
                    if times <= 0:
                        break
        except Exception as e:
            self.off()
            del randint,choice
            raise e

#-----------------------
# end
#-----------------------
