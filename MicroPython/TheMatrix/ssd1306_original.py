# I don't use this script anymore.
# I changed to another ssd1306 script that also handles i2c.
# The file has the same name as this one, so it's confusing.

# notify
print('LOAD: ssd1306.py')

import time
from machine import Pin, SPI
from math import sin, cos, radians

class SSD1306_128X64_GRID:

    ############################
    # variables
    ############################

    # Note: Some modules require 3.3V (charge pump is active). Will be blank with 5V.
    # See command below: Enable charge pump regulator 8Dh, 14h

    # IOMUX pins for SPI controllers
    # Note: Port 1 for 80Mhz (otherwise 40 max)
    # Note: Only the first device attaching to the bus can use CS0 pin.
    #          HSPI  VSPI
    # Pin Name GPIO Number
    # CS0*     15     5
    # SCLK     14    18
    # MISO     12    19
    # MOSI     13    23
    # QUADWP    2    22
    # QUADHD    4    21

    # spi pins (including cs and dc, miso is not used)
    mosi = 23
    miso = 19 # not used
    sck  = 18
    cs   =  5
    dc   = 21 # this is a data/command switch used by the ssd1306

    # spi port
    port = 1
    baudrate = 10 * 1024 * 1024 # low rate to start (try x8 for max)
    polarity = 0
    phase = 0
    bits = 8
    firstbit = SPI.MSB

    # GRIDS:
   
    # FRAME:

    # frame is 128*64=8192 bytes
    width = 128
    height = 64
    pages = height//8
    fbytes = width*pages
    frame = bytearray(fbytes)

    # display variables 
    contrast_value = 255 # default to highest

    ############################
    # init
    ############################

    def __init__(self):

        pass

    ############################
    # port (SPI and ssd1306)
    ############################

    # open port
    def port_open(self,test=True):

        print(self.port,self.baudrate,self.polarity,self.phase,self.bits,self.firstbit,self.sck,self.miso,self.mosi)

        # port
        self.port = SPI(self.port,
                        baudrate=self.baudrate,
                        polarity=self.polarity,
                        phase=self.phase,
                        bits=self.bits,
                        firstbit=self.firstbit,
                        sck=Pin(self.sck),
                        mosi=Pin(self.mosi),
                        miso=Pin(self.miso))

        # CS
        self.CS = Pin(self.cs,mode=Pin.OUT)
        self.CS.value(1)

        # DC
        self.DC = Pin(self.dc,mode=Pin.OUT)
        self.DC.value(1)

        # setup ssd1306
        self.ssd1306init()
        self.port_clear()

        # test
        if test:
            #self.port_test()
            self.hypno()

    # ssd1306 init
    def ssd1306init(self):

        # Set MUX Ratio A8h 3Fh
        # Set Display Offset D3h 00h
        # Set Display Start Line 40h
        # Set Segment re-map A0h/A1h
        # Set COM Output Scan Direction C0h/C8h
        # Set Contrast Control 81h 7Fh
        self.command((0x81,self.contrast_value))
        # Disable Entire Display On A4h
        self.command((0xA4,))       
        # Set Normal Display A6h
        self.command((0xA6,))
        # Set Osc Frequency D5h 80h
        # Enable charge pump regulator 8Dh, 14h
        self.command((0x8D,0x14))       
        # Set COM Pins hardware configuration DAh 02
        # Display On AFh
        self.command((0xAF,))

        # Set Memory Addressing Mode
        self.command((0x20,0x00)) # horizontal addressing
        self.command((0x21,0,self.width-1)) # row start,end
        self.command((0x22,0,self.pages-1)) # page start,end

    # port close
    def port_close(self):

        # setup
        self.port_clear()
        self.off()        

        # port
        self.port.deinit()
        del self.port

        # CS
        Pin(self.cs,mode=Pin.IN)

        # DC
        Pin(self.dc,mode=Pin.IN)

    def port_clear(self):
        self.write((0,) * self.fbytes)
    
    # write data buffer to port
    def write(self,buffer):
        self.CS.value(1)
        self.DC.value(1)
        self.CS.value(0)
        self.port.write(bytearray(buffer))
        self.CS.value(1)

    # write command buffer to port
    def command(self,buffer):
        b = bytearray(buffer)
        #print('COMMAND:',b)
        self.CS.value(1)
        self.DC.value(0)
        self.CS.value(0)
        self.port.write(b)
        self.CS.value(1)
        self.DC.value(1)

    def contrast(self,c=None):
        if c != None:
            self.contrast_value = c
        self.command((0x81,self.contrast_value))

    def on(self):
        self.command((0xAF,))

    def off(self):
        self.command((0xAE,))

    def invert(self):
        self.command((0xA7,))

    def uninvert(self):
        self.command((0xA6,))

    # rotate on y axis
    def mirror(self):
        self.command((0xA1,))
    def unmirror(self):
        self.command((0xA0,))

    # rotate on x-axis
    def flip(self):
        self.command((0xC8,))
    def unflip(self):
        self.command((0xC0,))

    # rotate on x and y axis
    def r180(self):
        self.command((0xC8,))
        self.command((0xA1,))
    def unr180(self):
        self.command((0xC0,))
        self.command((0xA0,))

    ############################
    # frame 
    ############################

    def frame_clear(self):
        self.frame = bytearray(self.fbytes)

    def frame_fill(self):
        self.frame = bytearray((0xFF,)*self.fbytes)

    def frame_show(self):
        
        self.command((0x21,0,self.width-1)) # row start,end
        self.command((0x22,0,self.pages-1)) # page start,end

        self.write(self.frame)
    
    def bitset(self,X,Y,value=1):

        # full grid
        # starting from top-left corner as (1,1)
        # ending at bottom-right corner as (self.width,self.height)

        ### values in range
        ##if 1 <= X <= self.width and 1 <= Y <= self.height:
        ##
        ##    # r is the column, just X-1
        ##    r = X-1
        ##
        ##    # p is the page (0-7)
        ##    p = (Y-1)//8
        ##
        ##    # b is the bit (0-1)
        ##    b = (Y-1)%8
        ##
        ##    # B is the byte to change
        ##    B = (p * 128) + r
        ##
        ##    # set
        ##    if value:
        ##        self.frame[B] |= (2**b)
        ##
        ##    # clear
        ##    else:
        ##        self.frame[B] &= ~(2**b)

        if X < 1:
            return
        if X > self.width:
            return
        if Y < 1:
            return
        if Y > self.height:
            return

        if value:
            self.frame[(((Y-1)//8)*self.width)+(X-1)] |=  (2**((Y-1)%8))

        else:
            self.frame[(((Y-1)//8)*self.width)+(X-1)] &= ~(2**((Y-1)%8))
                

    def bitclear(self,X,Y,value=0):

        self.bitset(X,Y,0)

    ############################
    # shapes 
    ############################

    def hline(self,X,Y,L,value=1):
        if L >= 0:
            if value:
                for x in range(X,X+L+1):
                    self.bitset(x,Y)
            else:
                for x in range(X,X+L+1):
                    self.bitclear(x,Y)
        else:
            if value:
                for x in range(X,X+L-1,-1):
                    self.bitset(x,Y)
            else:
                for x in range(X,X+L-1,-1):
                    self.bitclear(x,Y)
            
    def vline(self,X,Y,L,value=1):
        if L >= 0:
            if value:
                for y in range(Y,Y+L+1):
                    self.bitset(X,y)
            else:
                for y in range(Y,Y+L+1):
                    self.bitclear(X,y)
        else:
            if value:
                for y in range(Y,Y+L-1,-1):
                    self.bitset(X,y)
            else:
                for y in range(Y,Y+L-1,-1):
                    self.bitclear(X,y)

    def line(self,X1,Y1,X2,Y2,value=1):

        if X1 == X2:
            self.vline(X1,Y1,Y2-Y1,value)

        elif Y1 == Y2:
            self.hline(X1,Y1,X2-X1,value)

        else:

            m = (Y2-Y1)/(X2-X1)
            b = Y1 - m*X1

            if abs(m) <= 1:

                X1 = int(round(X1,0))
                X2 = int(round(X2,0))

                if X1 > X2:
                    X1,X2 = X2,X1

                for x in range(X1,X2+1):
                    y = int(round(m*x+b,0))

                    if value:
                        self.bitset(x,y)
                    else:
                        self.bitclear(x,y)

            else:

                Y1 = int(round(Y1,0))
                Y2 = int(round(Y2,0))

                if Y1 > Y2:
                    Y1,Y2 = Y2,Y1

                for y in range(Y1,Y2+1):
                    x = int(round((y-b)/m,0))

                    if value:
                        self.bitset(x,y)
                    else:
                        self.bitclear(x,y)

    def ray(self,X,Y,length=32,angle=45,value=1,draw=True):

        angle *= -(6.2832/360)

        x = int(round(X+length*cos(angle),0))
        y = int(round(Y+length*sin(angle),0))

        if draw:
            self.line(X,Y,x,y,value)

        return x,y

    def rect(self,X1,Y1,X2,Y2,value=1):

        # rectangle from top-left to bottom-right
        
        self.hline(X1,Y1,X2-X1,value)
        self.hline(X1,Y2,X2-X1,value)
        self.vline(X1,Y1,Y2-Y1,value)
        self.vline(X2,Y1,Y2-Y1,value)

    def poly(self,X,Y,R,value=1,sides=8,start=0,end=360):

        # draw multiple lines (sides)
        # centered on (X,Y)
        # radius R is distance from (X,Y) to line ends
        # start and end are angles from (X,Y) to arc ends in degrees
        # start to end is always counter-clockwise in degrees
        # end must be > start

        # circles = start 0, end 360, sides big enough to be smooth

        if start > end:
            start,end = end,start
        arc = (end-start)
        sideangle = arc/sides

        lastx,lasty = self.ray(X,Y,R,start,draw=False)

        while start < end:

            start += sideangle

            nextx,nexty = self.ray(X,Y,R,start,draw=False)

            self.line(lastx,lasty,nextx,nexty,value)

            lastx,lasty = nextx,nexty

        return lastx,lasty

    ############################
    # text 
    ############################

    # size 7 (height 7 pixels) base font (can be scaled by whole numbers)
    font  = ['   XXX XXXX  XXX XXXX XXXXXXXXXX XXX X   XXXX   XXX   XX    X     XX   X XXX XXXX  XXX XXXX  XXX XXXXXX   XX   XX     XX   XX   XXXXXX XXX  X  XXX  XXX     XXXXXX XXX XXXXX XXX  XXX X       XXXXXXX     X      X     X XXX  X X  XXX       X  XX   X   XX          XX  X X XX      X XXX ', '  X   XX   XX   XX   XX    X    X   XX   X X     XX  X X    XX   XXXX  XX   XX   XX   XX   XX   X  X  X   XX   XX     XX   XX   X    XX   XXX X   XX   XX   XX    X   X    XX   XX   X X      X    X X    X     X      XX   XXXXXXX X XX   XX XX  X XXX X  X        X  X X X X X    X X   X', '  X   XX   XX    X   XX    X    X    X   X X     XX X  X    X X X XX X XX   XX   XX   XX   XX      X  X   XX   XX     X X X  X X    X X   X X     X    XX   XX    X       X X   XX   X     XXXX    X  X  X     X     XXXX  XX X X X X     X    X  X  X X    X    X  X  X XX     X  X     X ', '  XXXXXXXXX X    X   XXXX  XXX  X  XXXXXXX X     XXX   X    X  X  XX  XXX   XXXXX X   XXXXX  XXX   X  X   XX   XX  X  X  X    X    X  X   X X    X   XX XXXXXXXXX XXXX   X   XXX  XXXX  XXX   X    X  X        X    X  XX X X X X  XXX   X     XXX     X    X   XXXX    X        XX     X  ', '  X   XX   XX    X   XX    X    X   XX   X X     XX X  X    X     XX   XX   XX    X X XX  X     X  X  X   XX   XX X X X X X   X   X   X   X X   X      X    X    XX   X X   X   X    X     XXXX    X  X        X  XX   XX  X XXXXX  X X X      X X X   X    X    X  X  X X      X  X    X  ', '  X   XX   XX   XX   XX    X    X   XX   X X X   XX  X X    X     XX   XX   XX    X  X X   XX   X  X  X   X X X XX   XXX   X  X  X    X   X X  X   X   X    XX   XX   X X   X   XX   X        X    X   X X X  X         X     X X X X XX   X   X  X     X  X        X  X XX    X    X      ', '  X   XXXXX  XXX XXXX XXXXXX     XXX X   XXXX XXX X   XXXXXXX     XX   X XXX X     XX XX   X XXX   X   XXX   X  X     XX   X  X  XXXXX XXX XXXXXXXX XXX     X XXX  XXX  X    XXX  XXX         XXXXXX    XX XXX         X XXX       XXX          XX X     XX  XXX     XX  X    X      X  X  '] #
    chars = {'height': 7, 'gap': 1, 'invert': False, ' ': (' ', 2, 0), 'A': ('A', 5, 2), 'B': ('B', 5, 7), 'C': ('C', 5, 12), 'D': ('D', 5, 17), 'E': ('E', 5, 22), 'F': ('F', 5, 27), 'G': ('G', 5, 32), 'H': ('H', 5, 37), 'I': ('I', 3, 42), 'J': ('J', 5, 45), 'K': ('K', 5, 50), 'L': ('L', 5, 55), 'M': ('M', 7, 60), 'N': ('N', 5, 67), 'O': ('O', 5, 72), 'P': ('P', 5, 77), 'Q': ('Q', 5, 82), 'R': ('R', 5, 87), 'S': ('S', 5, 92), 'T': ('T', 5, 97), 'U': ('U', 5, 102), 'V': ('V', 5, 107), 'W': ('W', 7, 112), 'X': ('X', 5, 119), 'Y': ('Y', 5, 124), 'Z': ('Z', 5, 129), '0': ('0', 5, 134), '1': ('1', 3, 139), '2': ('2', 5, 142), '3': ('3', 5, 147), '4': ('4', 5, 152), '5': ('5', 5, 157), '6': ('6', 5, 162), '7': ('7', 5, 167), '8': ('8', 5, 172), '9': ('9', 5, 177), '`': ('`', 2, 182), '-': ('-', 3, 184), '=': ('=', 3, 187), '[': ('[', 3, 190), ']': (']', 3, 193), '\\': ('\\', 5, 196), ';': (';', 1, 201), "'": ("'", 1, 202), ',': (',', 1, 203), '.': ('.', 1, 204), '/': ('/', 5, 205), '~': ('~', 5, 210), '!': ('!', 1, 215), '@': ('@', 5, 216), '#': ('#', 5, 221), '$': ('$', 5, 226), '%': ('%', 5, 231), '^': ('^', 3, 236), '&': ('&', 5, 239), '*': ('*', 3, 244), '(': ('(', 3, 247), ')': (')', 3, 250), '_': ('_', 3, 253), '+': ('+', 3, 256), '{': ('{', 3, 259), '}': ('}', 3, 262), '|': ('|', 1, 265), ':': (':', 1, 266), '"': ('"', 3, 267), '<': ('<', 4, 270), '>': ('>', 4, 274), '?': ('?', 5, 278)} #

    def place_text(self,text,X,Y,scale=1,center=True,middle=True,value=1):

        # unscaled
        char_height = self.chars['height']
        char_gap    = self.chars['gap'   ]

        text = str(text).upper()
        text = ''.join([c for c in text if c in self.chars])
        text = ' '.join(text.split())

        #print('TEXT:',[text],scale)

        if text:

            X = int(round(X,0))
            Y = int(round(Y,0))

            if middle:
                Y = max(Y-int(scale*char_height/2),1)

            if center:
                tlen = int((sum([self.chars[c][1] for c in text]) + (len(text)-1)*char_gap)*scale)
                X = max(X-tlen//2,1)
            
            xindex = 0           
            for c in text:
                c2,cwidth,cindex = self.chars[c]
                for x in range(cwidth):
                    cX = cindex + x
                    for xscale in range(scale):
                        tX = xindex + X
                        yindex = char_height * scale
                        for cY in range(char_height-1,-1,-1):
                            for yscale in range(scale):
                                if self.font[cY][cX] in ('X','#'): #
                                    tY = Y + yindex
                                    if value:
                                        self.bitset(tX,tY)
                                    else:
                                        self.bitclear(tX,tY)
                                yindex -= 1
                        xindex += 1
                xindex += int(char_gap*scale)
                if xindex + X >= self.width:
                    break

    ############################
    # animations and other sugar
    ############################

    def canvas(self,value=0):

        # make a canvas of given value
        # prep for writing, does not send to port

        if value:
            self.frame_fill()
        else:
            self.frame_clear()

    def clear(self,value=0):

        # value is target canvas value
        # i.e. the "clear to" value
        # normally 0
        
        self.canvas(value)
        self.frame_show()

    def clear2(self,value=0,border=True):

        # value is target canvas value
        # i.e. the "clear to" value
        # normally 0
        
        X1 = 0
        Y1 = 0
        X2 = self.width+1
        Y2 = self.height+1

        if value:
            notvalue = 0
        else:
            notvalue = 1

        while Y1<Y2:
            self.rect(X1,Y1,X2,Y2,value)
            if border and Y1<Y2+2:
                self.rect(X1+1,Y1+1,X2-1,Y2-1,notvalue)
            self.frame_show()
            X1 += 1
            Y1 += 1
            X2 -= 1
            Y2 -= 1

        self.canvas(value)
        self.frame_show()

    def border(self,value=1):
        self.rect(1,1,self.width,self.height,value)
           
    def hide(self):
        self.port_clear()

    def show(self):
        self.frame_show()

    def fadein(self,pause=0.005):
        self.command((0x81,0))
        self.frame_show()
        for x in range(1,self.contrast_value+1):
            self.command((0x81,x))
            time.sleep(pause)

    def fadeout(self,pause=0.005):
        for x in range(self.contrast_value,-1,-1):
            self.command((0x81,x))
            time.sleep(pause)
        self.port_clear()

    def fadeinout(self,wait=2,pause=0.005):
        self.fadein(pause)
        time.sleep(wait)
        self.fadeout(pause)

    def test(self):
        self.frame_clear()
        self.rect(1,1,128,64,1)
        self.frame_show()
        for X in range(1,128,1):
            self.vline(X,0,64,value=1)
            self.frame_show()
            #time.sleep(0.1)
        self.frame_clear()
        self.rect(1,1,128,64,1)
        self.frame_show()
        for Y in range(1,64,1):
            self.hline(0,Y,128,value=1)
            self.frame_show()
            #time.sleep(0.1)
        self.frame_clear()
        self.port_clear()

    def countdown(self,start=3,value=1):

        X = self.width//2
        Y = self.height//2
        R = Y-1

        if value:
            notvalue = 0
        else:
            notvalue = 1

        self.canvas(notvalue)

        for N in range(start,0,-1):
            for A in range(0,361,45):
                self.canvas(notvalue)
                self.ray(X,Y,R,A,value)
                self.poly(X,Y,R,value,max(R/2,8),start=0,end=A)
                self.place_text(N,X,Y,3,True,True,value)
                self.frame_show()
                #time.sleep_ms(100)

        self.canvas(notvalue)
        self.frame_show()

    def randomflash(self,count=1024,pause=0.01):
        import random
        i1 = self.contrast_value
        self.canvas(0)
        try:
            c = 0
            while 1:
                x = random.randint(1,self.width)
                y = random.randint(1,self.height)
                self.contrast(random.randint(0,255))
                self.bitset(x,y)
                self.frame_show()
                time.sleep(pause)
                self.bitclear(x,y)
                self.frame_show()
                c += 1
                if c >= count:
                    break
        except KeyboardInterrupt:
            pass

        self.contrast(i1)
        self.canvas(0)
        self.frame_show()

    def hypno(self,count=0,value=1):
        import random
        if value:
            notvalue = 0
        else:
            notvalue = 1        
        try:
            c = 0
            Rmax = self.height
            while 1:
                X = random.randint(16,self.width-16)
                Y = random.randint(16,self.height-16)
                for R in range(Rmax,0,-8):
                    self.canvas(notvalue)
                    self.poly(X,Y,R,value,max(R/2,8))
                    self.frame_show()
                    #time.sleep_ms(100)
                c += 1
                if count and c >= count:
                    break
        except KeyboardInterrupt:
            pass
        self.canvas(notvalue)
        self.frame_show()

