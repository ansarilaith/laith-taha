import time
from machine import Pin, SPI
from math import sin, cos, radians

class MAX7219_16X16_GRID:

    ############################
    # variables
    ############################

    # this is for the TTGO-style ESP32 Dev Board
    # this is the pinout used for setup
    #                     ----
    #                    |    | RST
    #                    |    | 3V
    #                    |    | NC
    #                    |    | GND
    #                BAT |    | A00 DAC2
    #                 EN |    | A01 DAC1 
    #                USB |    | A02  G34 IN
    #            G13 A12 |    | A03  G39 IN
    #            G12 A11 |    | A04  G36 IN
    #            G27 A10 |    | A05  G04 --> CS
    #            G33 A09 |    | SCK  G05 --> SCK
    #            G15 A08 |    | MOSI G18 --> MOSI
    #            G32 A07 |    | MISO G19 --> MISO (not needed)
    #            G14 A06 |    | RX   G16 
    #            G22 SCL |    | TX   G17 
    #            G23 DSA |    |      G21 
    #                     ----

    # spi pins (including cs)
    mosi = 18
    sck = 5
    cs = 4

    # GRIDS:

    # input cascade: ESP32 --> grid 0 --> 1 --> 2 --> 3

    #       gridcol 0          gridcol 1
    #        grid 0             grid 2
    #         byte               byte
    #    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7

    # L  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    gridrow 0
    #    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # M  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0

    # L  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    gridrow 1
    #    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # M  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    # B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0

    #    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7
    #         byte               byte
    #        grid 1             grid 3
    #       gridcol 0          gridcol 1
    
    # FRAME:

    #         byte 0   byte 1   byte 2   byte 3   byte 4   byte 5   byte 6   byte 7  
    # grid 0 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 
    # grid 1 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 
    # grid 2 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 
    # grid 3 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000

    # frame is 32 bytes
    frame = bytearray(32)

    # display variables
    intensity = 0

    ############################
    # init
    ############################

    def __init__(self):

        pass

    ############################
    # port (SPI and max7219)
    ############################

    # open port
    def port_open(self,port=1,test=True):

        # port
        self.port = SPI(port, baudrate=10000000, polarity=1, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(self.sck), mosi=Pin(self.mosi))

        # CS
        self.CS = Pin(self.cs,mode=Pin.OUT)
        self.CS.value(1)

        # setup max7219
        self.max7219init()
        self.port_clear()

        # test
        if test:
            self.port_test()

    # max7219 init
    def max7219init(self):

        # setup (see MAX7219 specs)
        self.command((15,0))#;print('DISPLAY TEST OFF') # test mode off (do this first)
        self.command(( 9,0))#;print('DECODE MODE NONE') # decode mode off
        self.command((10,self.intensity))#;print('INTENSITY 0 / 15') # intensity lowest 
        self.command((11,7))#;print('SCAN LIMIT 7 ALL') # scan limit all
        self.on()

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

    # ALL WRITES == (location,value)
    # location 0 = noop
    # location 1-8 = display locations (byte)
    # location 9+ = command location

    # write buffer to port
    def write(self,buffer):
        #print('WRITE:',list(buffer))
        self.CS.value(0)
        self.port.write(buffer)
        self.CS.value(1)

    # write byte to one grid
    def write1(self,buffer,grid):
        self.write( bytearray((0,0)*(3-grid)) + bytearray(buffer) + bytearray((0,0)*grid) )

    # write command
    def command(self,buffer):
        self.write( bytearray(buffer*4) )

    def set_intensity(self,i=0):
        # intensity 0x0A: 00 to 0F
        # 0x0A = 10: 0-15
        #print('SET INTENSITY:',i)
        self.intensity = i
        self.command((10,self.intensity))

    def off(self):
        # shut down mode 0x0C: 0x00 or 0x01
        # 0x0C = 11: 0 or 1
        #print('PORT OFF')
        self.command((12,0))

    def on(self):
        # shut down mode 0x0C: 0x00 or 0x01
        # 0x0C = 11: 0 or 1
        #print('PORT ON')
        self.command((12,1))

    def port_clear(self):
        #print('PORT CLEAR')
        for row in range(1,9):
            self.command((row,0))
    
    def port_test(self):
        print('PORT TEST')
        
        i = self.intensity
        self.set_intensity(0)

        ranges = ((1,9,1),(9,17,1))

        for r1 in ranges:
            for r2 in ranges:
                self.frame_clear()
                for x in range(*r1):
                    for y in range(*r2):
                        self.bitset(x,y)
                self.frame_show()
                time.sleep_ms(1000)

        self.frame_clear()
        self.port_clear()

        self.set_intensity(i)

    ############################
    # frame 
    ############################

    def frame_clear(self):
        self.frame = bytearray(32)

    def frame_fill(self):
        self.frame = bytearray((0xFF,)*32)

    def frame_show(self):
        
        #self.max7219init()

        for y in range(8):
            self.write(bytearray( (y+1,self.frame[y+24]) + (y+1,self.frame[y+16]) + (y+1,self.frame[y+8]) + (y+1,self.frame[y]) ))
    
    def bitset(self,X,Y):

        # starting from top left corner as (1,1)
        # 16x16 grid

        # values in range
        if 1 <= X <= 16 and 1 <= Y <= 16:

            # col 0
            if X <= 8:

                # grid 0 (row 0)
                if Y <= 8:
                    self.frame[X-1] |= (2**(Y-1))

                # grid 1 (row 1)
                else:
                    self.frame[X-1+8] |= (2**(Y-1-8))

            # col 1
            else:
                
                # grid 2 (row 0)
                if Y <= 8:
                    self.frame[X-1-8+16] |= (2**(Y-1))

                # grid 3 (row 1)
                else:
                    self.frame[X-1-8+24] |= (2**(Y-1-8))

    def bitclear(self,X,Y):

        # starting from top left corner as (1,1)
        # 16x16 grid

        # values in range
        if 1 <= X <= 16 and 1 <= Y <= 16:

            # col 0
            if X <= 8:

                # grid 0 (row 0)
                if Y <= 8:
                    self.frame[X-1] &= ~(2**(Y-1))

                # grid 1 (row 1)
                else:
                    self.frame[X-1+8] &= ~(2**(Y-1-8))

            # col 1
            else:
                
                # grid 2 (row 0)
                if Y <= 8:
                    self.frame[X-1-8+16] &= ~(2**(Y-1))

                # grid 3 (row 1)
                else:
                    self.frame[X-1-8+24] &= ~(2**(Y-1-8))

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

    def circle(self,X,Y,R,value=1):
        self.poly(X,Y,R,value,8,0,360)

    def poly(self,X,Y,R,value=1,sides=8,start=0,end=360):

        # draw multiple lines (sides)
        # centered on (X,Y)
        # radius R is distance from (X,Y) to line ends
        # start and end are angles from (X,Y) to arc ends in degrees
        # start to end is always counter-clockwise in degrees
        # end must be > start

        # circles = start 0, end 360, sides big enough to be smooth

        # setup in radians
        radangle = 6.2832/360
        if start > end:
            start,end = end,start
        arc = (end-start)*radangle
        start *= radangle
        end   *= radangle
        sideangle = arc/(sides)

        lastx = int(round(X+R*sin(start),0))
        lasty = int(round(Y+R*cos(start),0))

        # draw from last point to current point
        while start < end:

            start = min(end,start+sideangle)

            nextx = int(round(X+R*sin(start),0))
            nexty = int(round(Y+R*cos(start),0))

            self.line(lastx,lasty,nextx,nexty,value)            

            lastx,lasty = nextx,nexty

    ############################
    # text 
    ############################

    font5  = [' ########### #################  ########   #    ', ' # ##  #  ## ##  #    ## ## ### ##  #  #   # #  ', ' # ##### ########### # ####### ####### # # #  ##', ' # ###    #  #  ## # # # #  ##  #  ##  ## ## #  ', ' ##########  ####### # #######  ########   ##   '] #
    chars5 = {'height': 5, 'gap': 1, 'invert': False, ' ': (' ', 1, 0), '0': ('0', 3, 1), '1': ('1', 1, 4), '2': ('2', 3, 5), '3': ('3', 3, 8), '4': ('4', 3, 11), '5': ('5', 3, 14), '6': ('6', 3, 17), '7': ('7', 3, 20), '8': ('8', 3, 23), '9': ('9', 3, 26), 'N': ('N', 4, 29), 'S': ('S', 3, 33), 'E': ('E', 3, 36), 'W': ('W', 5, 39), '.': ('.', 1, 44), ':': (':', 1, 45), '-': ('-', 2, 46)} #

    font7  = ['  XXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXX    ', '  X  XX   X   XX  XX   X      XX  XX  X X  ', '  X  XX   X   XX  XX   X     X X  XX  X    ', '  X  XXXXXX XXXXXXXXXXXXXXX X  XXXXXXXX  XX', '  X  XXX      X   X   XX  X X  X  X   X    ', '  X  XXX      X   X   XX  X X  X  X   X X  ', '  XXXXXXXXXXXXX   XXXXXXXXX X  XXXXXXXXX   '] #
    chars7 = {'height': 7, 'gap': 1, 'invert': False, ' ': (' ', 2, 0), '0': ('0', 4, 2), '1': ('1', 1, 6), '2': ('2', 4, 7), '3': ('3', 4, 11), '4': ('4', 4, 15), '5': ('5', 4, 19), '6': ('6', 4, 23), '7': ('7', 4, 27), '8': ('8', 4, 31), '9': ('9', 4, 35), '.': ('.', 1, 39), ':': (':', 1, 40), '-': ('-', 2, 41)} #

    font11  = ['  XXXXXXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX        ', '  XXXXXXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX        ', '  XX   XXXX     XX     XXXX   XXXX     XX          XXXX   XXXX   XX  XX    ', '  XX   XXXX     XX     XXXX   XXXX     XX         XX XX   XXXX   XX  XX    ', '  XX   XXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXXXXXXX   XX  XXXXXXXXXXXXXX        ', '  XX   XXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXXXXXXX  XX   XXXXXXXXXXXXXX    XXXX', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX        ', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX  XX    ', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX  XX    ', '  XXXXXXXXXXXXXXXXXXXXXXX     XXXXXXXXXXXXXXXX  XX   XXXXXXXXXXXXXXXX      ', '  XXXXXXXXXXXXXXXXXXXXXXX     XXXXXXXXXXXXXXXX  XX   XXXXXXXXXXXXXXXX      '] #
    chars11 = {'height': 11, 'gap': 2, 'invert': False, ' ': (' ', 2, 0), '0': ('0', 7, 2), '1': ('1', 2, 9), '2': ('2', 7, 11), '3': ('3', 7, 18), '4': ('4', 7, 25), '5': ('5', 7, 32), '6': ('6', 7, 39), '7': ('7', 7, 46), '8': ('8', 7, 53), '9': ('9', 7, 60), '.': ('.', 2, 67), ':': (':', 2, 69), '-': ('-', 4, 71)} #

    def place_text(self,text,X,Y,font=5,center=True,middle=True,value=1):

        if font == 11:
            font,chars = self.font11,self.chars11
        elif font == 7:
            font,chars = self.font7,self.chars7
        else:
            font,chars = self.font5,self.chars5
        char_height = chars['height']
        char_gap = chars['gap']

        text = text.upper()
        text = ''.join([c for c in text if c in chars])
        text = ' '.join(text.split())

        if text:

            X = int(X)
            Y = int(Y)

            if middle:
                Y = max(Y-char_height//2,1)

            if center:
                tlen = sum([chars[c][1] for c in text]) + (len(text)-1)*char_gap
                X = max(X-tlen//2,1)
            
            xindex = 0           
            for c in text:
                c2,cwidth,cindex = chars[c]
                for x in range(cwidth):
                    cX = cindex + x
                    tX = xindex + X
                    for cY in range(char_height-1,-1,-1):
                        if font[cY][cX] in ('X','#'): #
                            tY = cY + Y
                            if value:
                                self.bitset(tX,tY)
                            else:
                                self.bitclear(tX,tY) 
                    xindex += 1
                xindex += char_gap
                if xindex + X >= 16:
                    break

############################
# save 
############################

##mirror = False
##flip = False

### reverse byte lookup table
### MSB --> LSB or LSB --> MSB
##rbyte = [0,128,64,192,32,160,96,224,16,144,80,208,48,176,112,240,8,136,72,200,40,168,104,232,24,152,88,216,56,184,120,248,4,132,68,196,36,164,100,228,20,148,84,212,52,180,116,244,12,140,76,204,44,172,108,236,28,156,92,220,60,188,124,252,2,130,66,194,34,162,98,226,18,146,82,210,50,178,114,242,10,138,74,202,42,170,106,234,26,154,90,218,58,186,122,250,6,134,70,198,38,166,102,230,22,150,86,214,54,182,118,246,14,142,78,206,46,174,110,238,30,158,94,222,62,190,126,254,1,129,65,193,33,161,97,225,17,145,81,209,49,177,113,241,9,137,73,201,41,169,105,233,25,153,89,217,57,185,121,249,5,133,69,197,37,165,101,229,21,149,85,213,53,181,117,245,13,141,77,205,45,173,109,237,29,157,93,221,61,189,125,253,3,131,67,195,35,163,99,227,19,147,83,211,51,179,115,243,11,139,75,203,43,171,107,235,27,155,91,219,59,187,123,251,7,135,71,199,39,167,103,231,23,151,87,215,55,183,119,247,15,143,79,207,47,175,111,239,31,159,95,223,63,191,127,255]

### mirrored
##if self.mirror:
##
##    # mirrored and flipped
##    if self.flip:
##        for y in range(8):
##            self.write(bytearray( (8-y,self.frame[y+8]) + (8-y,self.frame[y]) + (8-y,self.frame[y+24]) + (8-y,self.frame[y+16]) ))
##
##    # just mirrored
##    # send 
##    else:
##        for y in range(8):
##            self.write(bytearray( (8-y,self.frame[y+8]) + (8-y,self.frame[y]) + (8-y,self.frame[y+24]) + (8-y,self.frame[y+16]) ))
##
### not mirrored
##else:


