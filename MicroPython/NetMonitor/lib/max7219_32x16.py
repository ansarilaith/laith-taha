# notify
print('LOAD: max7219_32x16.py')

import sys,time
from machine import Pin, SPI
from math import sin, cos, radians, sqrt

class MAX7219_32X16_GRID:

    ############################
    # variables
    ############################

    # ESP32: IOMUX pins for SPI controllers
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

    # by default this is for the TTGO-style ESP32 Dev Board
    # this is the pinout used for setup if you don't change it
    #                     ----
    #                    |    | RST
    #                    |    | 3V
    #                    |    | NC
    #                    |    | GND
    #                BAT |    | A00 DAC2
    #                 EN |    | A01 DAC1 
    #                USB |    | A02  G34 IN
    #  MOSI1 <-- G13 A12 |    | A03  G39 IN
    #  MISO1 <-- G12 A11 |    | A04  G36 IN
    #            G27 A10 |    | A05  G04
    #            G33 A09 |    | SCK  G05 
    #    CS1 <-- G15 A08 |    | MOSI G18 --> MOSI2
    #            G32 A07 |    | MISO G19 --> MISO2
    #   SCK1 <-- G14 A06 |    | RX   G16 
    #    CS2 <-- G22 SCL |    | TX   G17 
    #   SCK2 <-- G23 DSA |    |      G21 
    #                     ----

    # spi pins (including cs)
    mosi = 13
    sck  = 14
    cs   = 15

    # spi port
    port = 1
    baudrate = 10 * 1024 * 1024 # low rate to start (try x8 for max)
    polarity = 0
    phase = 0
    bits = 8
    firstbit = SPI.MSB

    # OUTPUT
    # data is sent in 16 bit words which equal bytearray(y,xbyte) MSB first
    # y is the y address for a given grid 1-8
    # xbyte is the 8 x-value bits for the given grid
    # data for grid 7 must be sent first, followed by data for the other 7 grids
    # the data words are pushed down the line by the next word while CS is low

    # GRIDS:

    # input cascade: ESP32 --> grid 0 --> 1 --> 2 --> 3  then 4 --> 5 --> 6 --> 7
    # notice that the order is different from the original 16X16 class

    #        grid 0             grid 1             grid 2             grid 3
    #
    #    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7

    #  L  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #     0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    gridrow 0
    #     0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  M  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0 ->
    #                                                                                |
    #                                                                                |
    #  ---- <-- ------------------------------------------------------------ <-- ----
    # |
    # |
    #  -> 0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  M  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    gridrow 1
    #     0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  M  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  S  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
    #  B  0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0    0 0 0 0 0 0 0 0

    #    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7    0 1 2 3 4 5 6 7
    #
    #        grid 4             grid 5             grid 6             grid 7
    
    # FRAME:
    # the frame mimics the grid for easy bitset lookups
    #       X 1-8    X 9-16   X 17-24  X 25-32  
    # Y  1 00000000 00000000 00000000 00000000
    # Y  2 00000000 00000000 00000000 00000000
    # Y  3 00000000 00000000 00000000 00000000
    # Y  4 00000000 00000000 00000000 00000000
    # Y  5 00000000 00000000 00000000 00000000
    # Y  6 00000000 00000000 00000000 00000000
    # Y  7 00000000 00000000 00000000 00000000
    # Y  8 00000000 00000000 00000000 00000000
    #-----------------------------------------
    # Y  9 00000000 00000000 00000000 00000000
    # Y 10 00000000 00000000 00000000 00000000
    # Y 11 00000000 00000000 00000000 00000000
    # Y 12 00000000 00000000 00000000 00000000
    # Y 13 00000000 00000000 00000000 00000000
    # Y 14 00000000 00000000 00000000 00000000
    # Y 15 00000000 00000000 00000000 00000000
    # Y 16 00000000 00000000 00000000 00000000

    # to send, send 8 blocks of data, one block for each Y address in a grid
    # each block has 1) a grid Y address (1-8) and 2) a byte of X address value, per grid
    # for each Y, the lower values start at (Y-1)*4, the uppers start 32 bytes higher
    
    # frame is 64 bytes
    frame = bytearray(64)

    # display variables
    intensity = 1

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
        self.port = SPI(self.port,baudrate=self.baudrate,polarity=self.polarity,phase=self.phase,bits=self.bits,firstbit=self.firstbit,sck=Pin(self.sck),mosi=Pin(self.mosi))

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
        self.write( bytearray((0,0)*(7-grid)) + bytearray(buffer) + bytearray((0,0)*grid) )

    # write command
    def command(self,buffer):
        self.write(bytearray(buffer*8))

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
    
    ############################
    # frame 
    ############################

    def frame_clear(self):
        self.frame = bytearray(64)

    def frame_fill(self):
        self.frame = bytearray((0xFF,)*64)

    def frame_show(self):

        self.max7219init()

        for y in range(1,9):
            lowers = (y-1)*4
            uppers = lowers+32
            self.write(bytearray((y,self.frame[uppers+3])+\
                                 (y,self.frame[uppers+2])+\
                                 (y,self.frame[uppers+1])+\
                                 (y,self.frame[uppers  ])+\
                                 (y,self.frame[lowers+3])+\
                                 (y,self.frame[lowers+2])+\
                                 (y,self.frame[lowers+1])+\
                                 (y,self.frame[lowers  ])))

    def bitset(self,X,Y,value=1):

        # starting from top left corner as (1,1)
        # 32x16 grid

        if X < 1:
            return
        if X > 32:
            return
        if Y < 1:
            return
        if Y > 16:
            return

        if value:
            self.frame[((Y-1)*4)+((X-1)//8)] |=  (2**(7-((X-1)%8)))

        else:
            self.frame[((Y-1)*4)+((X-1)//8)] &= ~(2**(7-((X-1)%8)))

    def bitclear(self,X,Y):
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

    font5  = [' ########### ################ X XX  XXXX XXXXXX XXX XXXX XXX XX  X   XX  XXX XX XXXXX  XXXXXX XX XX   XX XX XXXX    X  XXXXX   X   X  X X  X X XXX  X X  X X XX        XX  XX XX    X X ', ' # ##  #  ## ##  #    ## ## #X XX XX  X XX  X  X  X X X   XX XX  XX XXXX XX XX XX XX XX   X X XX XX   XX XX X  X #  XXXX  XX  XX   XX XX XXXXXXX  X XX XX X X  X   X  X  X X    X  X X X', ' # ##### ########### # ######XXXXX X  X XXX XX XXXXXX X   XXX X  X X XX XXX XXXXX XXX XXX X X XX XX X X X  X  X   ##   X  X X     X  XXXXX X X XXX X     X  X  X  XXXX    X      XX    X', ' # ###    #  #  ## # # # #  #X XX XX  X XX  X  X XX X X X XX XX  X   XX  XX XX  XXXX X  X X X XX XXX XXX X X X   #   XXX  X  XX XX     X XXXXXX  XX X   X X X  X   X  X  X X    X  X  X ', ' ##########  ####### # ######X XXXX XXXX XXXX   XXX XXXX X X XXXXX   XX  X XXX    XX XXX  X XXX X X   XX X X XXX#      XXXX  XX XX    X X  X X XXXX      XX  XX XX     XX  X   X    X X '] #
    chars5 = {'height': 5, 'gap': 1, 'invert': False, ' ': (' ', 1, 0), '0': ('0', 3, 1), '1': ('1', 1, 4), '2': ('2', 3, 5), '3': ('3', 3, 8), '4': ('4', 3, 11), '5': ('5', 3, 14), '6': ('6', 3, 17), '7': ('7', 3, 20), '8': ('8', 3, 23), '9': ('9', 3, 26), 'A': ('A', 3, 29), 'B': ('B', 3, 32), 'C': ('C', 3, 35), 'D': ('D', 3, 38), 'E': ('E', 3, 41), 'F': ('F', 3, 44), 'G': ('G', 3, 47), 'H': ('H', 3, 50), 'I': ('I', 3, 53), 'J': ('J', 3, 56), 'K': ('K', 3, 59), 'L': ('L', 3, 62), 'M': ('M', 5, 65), 'N': ('N', 4, 70), 'O': ('O', 3, 74), 'P': ('P', 3, 77), 'Q': ('Q', 3, 80), 'R': ('R', 3, 83), 'S': ('S', 3, 86), 'T': ('T', 3, 89), 'U': ('U', 3, 92), 'V': ('V', 3, 95), 'W': ('W', 5, 98), 'X': ('X', 3, 103), 'Y': ('Y', 3, 106), 'Z': ('Z', 3, 109), '.': ('.', 1, 112), ':': (':', 1, 113), '-': ('-', 2, 114), '`': ('`', 1, 116), '=': ('=', 2, 117), '[': ('[', 2, 119), ']': (']', 2, 121), '\\': ('\\', 3, 123), ';': (';', 1, 126), "'": ("'", 1, 127), ',': (',', 1, 128), '/': ('/', 3, 129), '~': ('~', 2, 132), '!': ('!', 1, 134), '@': ('@', 3, 135), '#': ('#', 5, 138), '$': ('$', 3, 143), '%': ('%', 3, 146), '^': ('^', 3, 149), '&': ('&', 3, 152), '*': ('*', 1, 155), '(': ('(', 2, 156), ')': (')', 2, 158), '_': ('_', 2, 160), '+': ('+', 3, 162), '{': ('{', 3, 165), '}': ('}', 3, 168), '|': ('|', 1, 171), '"': ('"', 3, 172), '<': ('<', 3, 175), '>': ('>', 3, 178), '?': ('?', 3, 181)} #

    font7  = ['   XX XXX  XX XXX XXXXXXXX XX X  XXXX  XXX  XX   X   XX  X XX XXX  XX XXX  XX XXXXXX  XX   XX   XX   XX   XXXXXX XXX  X  XXX  XXX     XXXXXX XXX XXXXX XXX  XXX X       XXXXXX    X          X XXX  X X  XXX XX    X  XX   X   XX          XX  X X XX      X XXX ', '  X  XX  XX  XX  XX   X   X  XX  X X    XX X X   XX XXXX XX  XX  XX  XX  XX  X  X  X  XX   XX   XX   XX   X    XX   XXX X   XX   XX   XX    X   X    XX   XX   X X      X    XX   X    X     XX   XXXXXXX X XXX  XX XX  X XXX X  X        X  X X X X X    X X   X', '  X  XX  XX   X  XX   X   X   X  X X    XXX  X   X X XX XXX  XX  XX  XX  XX     X  X  XX   XX   X X X  X X    X X   X X     X    XX   XX    X       X X   XX   X     XXXX    X X X    X XXX  XX X X X X X X     X    X  X  X X    X    X  X  X XX     X  X     X ', '  XXXXXXX X   X  XXXX XXX X XXXXXX X    XXX  X   X   XX  XX  XXXX X  XXXX  XX   X  X  XX   XX X X  X    X    X  X   X X    X   XX XXXXXXXXX XXXX   X   XXX  XXXX  XXX   X    X X      X   XXXXX XX  X X  XXX   X      XX     X    X   XXXX    X        XX     X  ', '  X  XX  XX   X  XX   X   X  XX  X X    XX X X   X   XX  XX  XX   X  XX X    X  X  X  XX   XX X X X X   X   X   X   X X   X      X    X    XX   X X   X   X    X     XXXX    X X      X      XX    XXXXX  X X X      X   X   X    X    X  X  X X      X  X    X  ', '  X  XX  XX  XX  XX   X   X  XX  X X X  XX  XX   X   XX  XX  XX   X X X  XX  X  X  X  X X X XX XXX   X  X  X    X   X X  X   X   X    XX   XX   X X   X   XX   X        X    X  XX X X        X   X X X X X XX  XX   X  X     X  X        X  X XX    X    X      ', '  X  XXXX  XX XXX XXXXX    XXXX  XXXX XX X  XXXXXX   XX  X XX X    X XX  X XX   X   XX   X  X   XX   X  X  XXXXX XXX XXXXXXXX XXX     X XXX  XXX  X    XXX  XXX         XXXXXX   X XX        X XXX       XXX    XX    XX X     XX  XXX     XX  X    X      X  X  '] #
    chars7 = {'height': 7, 'gap': 1, 'invert': False, ' ': (' ', 2, 0), 'A': ('A', 4, 2), 'B': ('B', 4, 6), 'C': ('C', 4, 10), 'D': ('D', 4, 14), 'E': ('E', 4, 18), 'F': ('F', 4, 22), 'G': ('G', 4, 26), 'H': ('H', 4, 30), 'I': ('I', 3, 34), 'J': ('J', 4, 37), 'K': ('K', 4, 41), 'L': ('L', 4, 45), 'M': ('M', 5, 49), 'N': ('N', 4, 54), 'O': ('O', 4, 58), 'P': ('P', 4, 62), 'Q': ('Q', 4, 66), 'R': ('R', 4, 70), 'S': ('S', 4, 74), 'T': ('T', 5, 78), 'U': ('U', 4, 83), 'V': ('V', 5, 87), 'W': ('W', 5, 92), 'X': ('X', 5, 97), 'Y': ('Y', 5, 102), 'Z': ('Z', 5, 107), '0': ('0', 5, 112), '1': ('1', 3, 117), '2': ('2', 5, 120), '3': ('3', 5, 125), '4': ('4', 5, 130), '5': ('5', 5, 135), '6': ('6', 5, 140), '7': ('7', 5, 145), '8': ('8', 5, 150), '9': ('9', 5, 155), '`': ('`', 2, 160), '-': ('-', 3, 162), '=': ('=', 3, 165), '[': ('[', 3, 168), ']': (']', 3, 171), '\\': ('\\', 3, 174), ';': (';', 1, 177), "'": ("'", 1, 178), ',': (',', 1, 179), '.': ('.', 1, 180), '/': ('/', 3, 181), '~': ('~', 5, 184), '!': ('!', 1, 189), '@': ('@', 5, 190), '#': ('#', 5, 195), '$': ('$', 5, 200), '%': ('%', 5, 205), '^': ('^', 3, 210), '&': ('&', 5, 213), '*': ('*', 3, 218), '(': ('(', 3, 221), ')': (')', 3, 224), '_': ('_', 3, 227), '+': ('+', 3, 230), '{': ('{', 3, 233), '}': ('}', 3, 236), '|': ('|', 1, 239), ':': (':', 1, 240), '"': ('"', 3, 241), '<': ('<', 4, 244), '>': ('>', 4, 248), '?': ('?', 5, 252)} #

    #font11  = ['   XXXXX XX XXXXX  XXXXX      XXXXXXXXX XXXXX XXXXXXX XXXXX  XXXXX         ', '  XXXXXXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX        ', '  XX   XXXX     XX     XXXX   XXXX     XX          XXXX   XXXX   XX  XX    ', '  XX   XXXX     XX     XXXX   XXXX     XX         XX XX   XXXX   XX  XX    ', '  XX   XXXX XXXXXX  XXXX XXXXXXXXXXXXX  XXXXX    XX   XXXXX XXXXXXX        ', '  XX   XXXXXXXXXX   XXXX XXXXXXXXXXXXXX XXXXXX  XX    XXXXX  XXXXXX    XXXX', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX        ', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX  XX    ', '  XX   XXXXXX          XX     XX     XXXX   XX  XX   XX   XX     XX  XX    ', '  XXXXXXXXXXXXXXXXXXXXXXX     XXXXXXXXXXXXXXXX  XX   XXXXXXXXXXXXXXXX      ', '   XXXXX XXXXXXXXX XXXXX      XX XXXXX  XXXXX   XX    XXXXX  XXXXX XX      '] #
    #chars11 = {'height': 11, 'gap': 2, 'invert': False, ' ': (' ', 2, 0), '0': ('0', 7, 2), '1': ('1', 2, 9), '2': ('2', 7, 11), '3': ('3', 7, 18), '4': ('4', 7, 25), '5': ('5', 7, 32), '6': ('6', 7, 39), '7': ('7', 7, 46), '8': ('8', 7, 53), '9': ('9', 7, 60), '.': ('.', 2, 67), ':': (':', 2, 69), '-': ('-', 4, 71)} #

    font16  = ['   XXXXXXX XX XXXXXXX  XXXXXXX        XXXXXXXXXXX XXXXXXX  XXXXXXXX XXXXXXX  XXXXXXX           ', '  XXXXXXXXXXXXXXXXXXXXXXXXXXXXX       XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX          ', '  XX     XXXX       XX       XXXX     XXXX       XX              XXXX     XXXX     XX          ', '  XX     XXXX       XX       XXXX     XXXX       XX             XX XX     XXXX     XX          ', '  XX     XXXX       XX       XXXX     XXXX       XX            XX  XX     XXXX     XX  XX      ', '  XX     XXXX       XX       XXXX     XXXX       XX           XX   XX     XXXX     XX  XX  XX  ', '  XX     XXXX       XX       XXXX     XXXX       XX          XX    XX     XXXX     XX      XX  ', '  XX     XXXX XXXXXXXX    XXXX XXXXXXXXXXXXXXXXX XXXXXXXX   XX      XXXXXXX XXXXXXXXX    XXXXXX', '  XX     XXXXXXXXXXXX     XXXX XXXXXXXXXXXXXXXXXXXXXXXXXXX XX       XXXXXXX  XXXXXXXX    XXXXXX', '  XX     XXXXXX              XX       XX       XXXX     XX XX      XX     XX       XX      XX  ', '  XX     XXXXXX              XX       XX       XXXX     XX XX      XX     XX       XX  XX  XX  ', '  XX     XXXXXX              XX       XX       XXXX     XX XX      XX     XX       XX  XX      ', '  XX     XXXXXX              XX       XX       XXXX     XX XX      XX     XX       XX          ', '  XX     XXXXXX              XX       XX       XXXX     XX XX      XX     XX       XX          ', '  XXXXXXXXXXXXXXXXXXXXXXXXXXXXX       XXXXXXXXXXXXXXXXXXXX XX      XXXXXXXXXXXXXXXXXXXX        ', '   XXXXXXX XXXXXXXXXXX XXXXXXX        XX XXXXXXX  XXXXXXX  XX       XXXXXXX  XXXXXXX XX        '] #
    chars16 = {'height': 16, 'gap': 2, 'invert': False, ' ': (' ', 2, 0), '0': ('0', 9, 2), '1': ('1', 2, 11), '2': ('2', 9, 13), '3': ('3', 9, 22), '4': ('4', 9, 31), '5': ('5', 9, 40), '6': ('6', 9, 49), '7': ('7', 9, 58), '8': ('8', 9, 67), '9': ('9', 9, 76), '.': ('.', 2, 85), ':': (':', 2, 87), '-': ('-', 6, 89)} #

    def place_text(self,text,X,Y,font=5,center=True,middle=True,value=1):

        # make font
        #if font == 11:
        #    font,chars = self.font11,self.chars11
        if font == 16:
            font,chars = self.font16,self.chars16
        elif font == 7:
            font,chars = self.font7,self.chars7
        else:
            font,chars = self.font5,self.chars5
        #font,chars = self.font7,self.chars7
        char_height = chars['height']
        char_gap    = chars['gap']

        # fix text
        text = str(text).upper()
        text = ''.join([c for c in text if c in chars])
        #text = ' '.join(text.split())
        print('PLACE:',[text])

        if text:

            X = int(round(X,0))
            Y = int(round(Y,0))

            if middle:
                Y = max(Y-char_height//2,1)
                if char_height%2 == 0:
                    Y += 1

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
                if xindex + X >= 32:
                    break

    def scroll_text(self,text,
                    Y,
                    font=5,
                    middle=True,
                    value=1,
                    count=1,
                    pause=100,
                    padfront=True,padback=True,
                    preclear=True,postclear=True, # clear before/after scrolling
                    leaveit=False, # don't clear last frame on exit
                    canvasit=False # use self.canvas to clear between frames
                    ):

        # make font
        #if font == 11:
        #    font,chars = self.font11,self.chars11
        if font == 16:
            font,chars = self.font16,self.chars16
        elif font == 7:
            font,chars = self.font7,self.chars7
        else:
            font,chars = self.font5,self.chars5
        #font,chars = self.font7,self.chars7
        char_height = chars['height']
        char_gap    = chars['gap']

        # fix text
        text = str(text).upper()
        text = ''.join([c for c in text if c in chars])
        #text = ' '.join(text.split())
        print('SCROLL:',[text])

        # make canvas
        if value:
            notvalue = 0
        else:
            notvalue = 1
        if preclear:
            self.canvas(notvalue)

        if text:

            Y = int(round(Y,0))

            if middle:
                Y = max(Y-char_height//2,1)
                if char_height%2 == 0:
                    Y += 1

            # make line
            line = []
            for x in range(char_height):
                line.append([])
            if padfront:
                for x in range(char_height):
                    line[x] += [0]*32                
            for c in text:
                c2,cwidth,cindex = chars[c]
                for x in range(cwidth):
                    cX = cindex + x
                    for cY in range(char_height):
                        #print(c,c2,cX,cY,[font[cY][cX]],font[cY][cX] in ('X','#')) #
                        if font[cY][cX] in ('X','#'): #
                            line[cY].append(1)
                        else:
                            line[cY].append(0)
                for x in range(char_gap):
                    for cY in range(char_height):
                        line[cY].append(0)
            if padback:
                for x in range(char_height):
                    line[x] += [0]*32
            line_len = len(line[0])
            #for l in line:
            #    print('LINE:',l[:120])

            # scroll
            loops = 0
            next_loop = time.ticks_ms()
            while 1:

                # blocks
                for start in range(max(1,line_len-32)):

                    # wait until next loop
                    while time.ticks_diff(next_loop,time.ticks_ms()) > 0:
                        time.sleep_ms(pause//10)
                    next_loop += pause

                    # clear previous bit sets
                    if canvasit:
                        self.canvas(notvalue)
                    elif start != 1:
                        for cY in range(char_height):
                            X = 1
                            for bit in line[cY][start-1:start-1+32]:
                                if bit==1:
                                    self.bitset(X,cY+Y,notvalue)
                                X += 1

                    # set new bits
                    for cY in range(char_height):
                        X = 1
                        for bit in line[cY][start:start+32]:
                            if bit==1:
                                self.bitset(X,cY+Y,value)
                                #print('SET:',(X,cY+Y))
                            X += 1

                    # show bits
                    self.frame_show()

                # final wait until nextloop
                while time.ticks_diff(next_loop,time.ticks_ms()) > 0:
                    time.sleep_ms(pause//10)
                next_loop += pause

                # final clear bits
                if not leaveit:
                    if canvasit:
                        self.canvas(notvalue)
                    else:
                        for cY in range(char_height):
                            X = 1
                            for bit in line[cY][start-1:start-1+32]:
                                if bit==1:
                                    self.bitset(X,cY+Y,notvalue)
                                X += 1

                # check loops
                loops += 1
                if count and loops >= count:
                    break

            # clear
            if postclear:
                self.canvas(notvalue)

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

    def show(self):
        self.frame_show()

    def port_test(self):
        print('PORT TEST')
        self.frame_clear()
        for X in range(1,33,1):
            self.vline(X,1,16,value=1)
            self.frame_show()
            self.frame_clear()
            time.sleep(0.01)
        self.frame_clear()
        for Y in range(1,17,1):
            self.hline(1,Y,32,value=1)
            self.frame_show()
            self.frame_clear()
            time.sleep(0.01)
        self.frame_clear()
        self.port_clear()

    def randomflash(self,count=256):
        import random
        i1 = self.intensity
        try:
            c = 0
            while 1:
                x = random.randint(1,32)
                y = random.randint(1,16)
                self.set_intensity(random.randint(0,15))
                self.bitset(x,y)
                self.frame_show()
                self.bitclear(x,y)
                self.frame_show()
                c += 1
                if c >= count:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.set_intensity(i1)

    def hypno(self,count=8):
        try:
            c = 0
            while 1:
                for r in range(32,0,-1):
                    self.canvas()
                    self.poly(16.5,8.5,r,1,max(8,r/2))
                    self.frame_show()
                    time.sleep(0.005)
                c += 1
                if count and c >= count:
                    break        
        except KeyboardInterrupt:
            pass

    def cclear(self):
        for r in range(20,-1,-1):
            for x in range(1,33):
                for y in range(1,17):
                    if sqrt((x-16)**2+(y-8)**2) >= r:
                        self.bitset(x,y,0)
            self.poly(16,8,r,1,8)
            self.frame_show()
        self.clear()

    def countdown(self,start=3,value=1):

        X = 16
        Y = 8
        R = 7

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
                self.place_text(N,X,Y,7,True,True,value)
                self.frame_show()
                time.sleep_ms(1000//8)

        self.canvas(notvalue)
        self.frame_show()

            
##    # ESP8266: The hardware SPI is faster (up to 80Mhz),
##    # but only works on following pins:
##    # MISO is GPIO12
##    # MOSI is GPIO13
##    # SCK is GPIO14
##    
##    # this is the ESP8266 D1 Mini pinout
##    #              -------
##    #         RST |     TX| G01 - TXD0
##    #        ADC0 |A0   RX| G03 - RXD0
##    # WAKE -  G16 |D0   D1| G05 - SCL
##    # SCLK -  G14 |D5   D2| G04 - SDA
##    # MISO -  G12 |D6   D3| G00 - FLASH
##    # MOSI -  G13 |D7   D4| G02
##    # CS   -  G15 |D8     | GND
##    #        3.3V |       | 5.0V
##    #              -------

