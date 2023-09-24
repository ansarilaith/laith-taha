#-----------------------
# notify
#-----------------------

print('LOAD: micropix.py')

#-----------------------
# imports
#-----------------------

import sys,time
from math import sin,cos,radians
from machine import Pin
from esp import neopixel_write

#-----------------------
# micropixel class
#-----------------------

class MicroPix:
    
    #-----------------------
    # init values
    #-----------------------

    # panel configuration for N panels
    #
    #         (1,1)      (2,1)      (N,1)      (panelx,panely)
    #
    #         |---|      |---|      |---|
    # in ---> | 1 | ---> | 2 | ---> | N | --->
    #         |---|      |---|      |---|    |
    #                                        |
    #    /---<---------------------------<---/
    #    | 
    #    |    (1,2)      (2,2)      (N,2)      (panelx,panely)
    #    | 
    #    |    |---|      |---|      |---|
    #    ---> |N+1| ---> |N+2| ---> |N+3| ---> out
    #         |---|      |---|      |---|

    # panel layout (how many columns = x, how many rows = y)
    panelx = 1 # default for 1 panel
    panely = 1 # detault for 1 row of panels
    pixelx = 8 # total width in pixels
    pixely = 8 # total height in pixels

    # default brightness out of 255
    bright = 4

    # origin is in TOP LEFT
    # origin is coordinates (0,0)
    # x axis positive is to the RIGHT
    # y axis positive is DOWN

    # index table lookup from x,y
    xy2it = []

    #-----------------------
    # color values
    #-----------------------

    # GRB bold colors
    colors = {
        'black':(0,0,0),
        'white':(255,255,225),
        'green':(255,0,0),
        'greener':(255,32,0),
        'lime':(255,64,0),
        'chartreuse':(255,128,0),
        'yellow':(225,255,0),
        'sunflower':(128,255,0),
        'orange':(64,255,0),
        'pumpkin':(32,255,0),
        'tomato':(16,255,0),
        'red':(0,255,0),
        'rose':(0,255,16),
        'fuchsia':(0,255,32),
        'magenta':(0,255,64),
        'pinker':(0,255,128),
        'pink':(0,255,255),
        'violet':(0,128,255),
        'ultra':(0,64,255),
        'indigo':(0,32,255),
        'blue':(0,0,255),
        'water':(32,0,255),
        'sky':(64,0,255),
        'azure':(128,0,255),
        'cyan':(255,0,255),
        'aqua':(255,0,128),
        'mint':(255,0,64),
        'grass':(255,0,32),
        }

    # get GBR bytearray
    def get_color(self,color,bright=None):

        # get color if not given
        if type(color) not in (list,tuple):
            color = self.colors.get(color,(0,255,0))

        # scale and return
        if bright:
            return bytearray([int(x*bright/255) for x in color])
        else:
            return bytearray([int(x*self.bright/255) for x in color])

    #-----------------------
    # init-deinit functions
    #-----------------------

    # init
    def __init__(self,pin,panelx,panely):

        # panel counts
        self.panelx = panelx
        self.panely = panely
        self.panelc = panelx * panely

        # pixel counts
        self.pixels = self.panelc * 64
        self.pixelx = 8 * panelx
        self.pixely = 8 * panely

        # create one byte array
        self.array = bytearray(self.pixels*3)

        # instantiate control pin    
        self.pin = pin
        self.p = Pin(self.pin,Pin.OUT)

    # de-init
    def kill(self):
        self.clear()
        Pin(self.pin,Pin.IN,pull=None)
        del self.array

    #-----------------------
    # control functions
    #-----------------------

    # set brightness
    def set_bright(self,bright=0):
        self.bright = min(255,abs(bright))

    #-----------------------
    # pixel functions
    #-----------------------

    # write buffer to data pin
    def write(self):
        neopixel_write(self.p,self.array,1)

    # all pixels off
    def clear(self,write=True):
        return self.fill('black',0,write)

    # all pixels on (faster than self.np.fill)
    def fill(self,color,bright=0,write=False):
        
        color = self.get_color(color,bright)

        for x in range(self.pixels):
            self.seti(x,color)

        if write:
            self.write()

    # get index from xy
    def xy2i(self,x,y):
        # 1) pannels above current row of pannels
        #    64 * self.panelx * (y//8)
        # 2) pannels before working pannel
        #    64 * (x//8)
        # 3) rows on current pannel above working row
        #    8 * (y%8)
        # 4) pixels before given pixel
        #    x%8
        # 5) everything combined
        return 64 * self.panelx * (y//8) + 64 * (x//8) + 8 * (y%8) + x%8
      
    # set a pixel at index to color
    def seti(self,index,color):
        self.array[index*3:index*3+3] = color

    # get color of pixel at index
    def geti(self,index):
        return self.array[index*3:index*3+3]

    # build a table of locations
    def make_xy2it(self):
        for x in range(self.pixelx):
            self.xy2it.append([self.xy2i(x,y) for y in range(self.pixely)])

    # set a pixel at (x,y)
    def setxy(self,x,y,color='red',bright=0,cfixed=False,write=False):

        # x and y within range
        if 0 <= x < self.pixelx and 0 <= y < self.pixely:

            # use xy2i table
            if self.xy2it:
                index = self.xy2it[x][y]

            # calculate
            else:
                index = self.xy2i(x,y)
                
            # get color
            if not cfixed:
                color = self.get_color(color)

            # set
            self.seti(index,color)

            # write
            if write:
                self.write()
            

##        # 1) pannels above current row of pannels
##        #    64 * self.panelx * (y//8)
##
##        # 2) pannels before working pannel
##        #    64 * (x//8)
##        
##        # 3) rows on current pannel above working row
##        #    8 * (y%8)
##
##        # 4) pixels before given pixel
##        #    x%8
##
##        # 5) everything combined
##        pixel = 64 * self.panelx * (y//8) + 64 * (x//8) + 8 * (y%8) + x%8
##
##        # insure correct range
##        if 0 <= pixel <= (self.pixels-1):
##
##            # get color
##            if not cfixed:
##                color = self.get_color(color)
##
##            # set
##            self.seti(pixel,color)
##
##            # write
##            if write:
##                self.write()

    #-----------------------
    # draw functions
    #-----------------------

    def hline(self,x,y,length,color='red',bright=0,write=False):

        # get color
        color = self.get_color(color,bright)

        # must have length
        if length:

            # direction    
            if length > 0:
                step = 1
                x2 = x + length + 1
            else:
                step = -1
                x2 = x + length - 1

            # iterate
            for x3 in range(x,x2,step):
                self.setxy(x3,y,color,cfixed=True,write=False)

            # write
            if write:
                self.write()

    def vline(self,x,y,length,color='red',bright=0,write=False):

        # get color
        color = self.get_color(color,bright)

        # must have length
        if length:

            # direction    
            if length > 0:
                step = 1
                y2 = y + length + 1
            else:
                step = -1
                y2 = y + length - 1

            # iterate
            for y3 in range(y,y2,step):
                self.setxy(x,y3,color,cfixed=True,write=False)

            # write
            if write:
                self.write()

    def line(self,x1,y1,x2,y2,color='red',bright=0,write=False):

        if x1 == x2:
            self.vline(x1,y1,y2-y1,color,bright,write)

        elif y1 == y2:
            self.hline(x1,y1,x2-x1,color,bright,write)

        else:

            # get color
            color = self.get_color(color,bright)

            # plot line
            for x,y in self.line_points(x1,y1,x2,y2,pos_only=True):
                self.setxy(x,y,color,cfixed=True,write=False)

            # write
            if write:
                self.write()

    def line_points(self,x1,y1,x2,y2):

        if x1 == x2:
            step = 1
            if y1 > y2:
                step = -1
            for y in range(y1,y2,step):
                yield x1,y

        elif y1 == y2:
            step = 1
            if x1 > x2:
                step = -1
            for x in range(x1,x2,step):
                yield x,y1

        else:

            # line values
            m = (y2-y1)/(x2-x1)
            b = y1 - m*x1

            # more change on x azis
            if abs(m) <= 1:

                if x1 > x2:
                    for x in range(x1,x2-1,-1):
                        yield x,int(round(m*x+b,0))

                else:
                    for x in range(x1,x2+1,1):
                        yield x,int(round(m*x+b,0))
                
            # more change on y axis
            else:

                if y1 > y2:
                    for y in range(y1,y2-1,-1):
                        yield int(round((y-b)/m,0)),y

                else:
                    for y in range(y1,y2+1,1):
                        yield int(round((y-b)/m,0)),y

    def rect(self,x1,y1,x2,y2,color='red',bright=0,write=False):

        # build
        self.hline(x1,y1,x2-x1,color,bright,write=False)
        self.hline(x1,y2,x2-x1,color,bright,write=False)
        self.vline(x1,y1,y2-y1,color,bright,write=False)
        self.vline(x2,y1,y2-y1,color,bright,write=False)

        # write
        if write:
            self.write()

    def ray(self,x,y,length=32,angle=45,color='red',bright=0,draw=True,write=False):

        # get end point
        angle = radians(angle)
        x2 = int(round(x+length*cos(angle),0))
        y2 = int(round(y+length*sin(angle),0))

        # add to buffer
        # handle write
        if draw:
            self.line(x1,y1,x2,y2,color,bright,write)

        # return end point
        else:
            return x2,y2

    def poly(self,x,y,r,sides=8,start=0,end=360,color='red',bright=0,write=False):

        # draw multiple lines (sides)
        # centered on (x,y)
        # radius r is distance from (x,y) to line ends
        # start and end are angles from (x,y) to arc ends in degrees
        # start to end is always counter-clockwise in degrees
        # end must be > start

        # circles = start 0, end 360, as many sides as needed to be smooth

        if start > end:
            start,end = end,start
        arc = (end-start)
        sideangle = arc/sides

        lastx,lasty = self.ray(x,y,r,start,draw=False)

        while start < end:
            start += sideangle
            nextx,nexty = self.ray(x,y,r,start,draw=False)
            self.line(lastx,lasty,nextx,nexty,color,bright,write=False)
            lastx,lasty = nextx,nexty
        
        # write
        if write:
            self.write()

    #-----------------------
    # text functions
    #-----------------------

    # base font (height 7 pixels) created using npxy_make_font_v2.py
    # dict {'height':7,'gap':1,character:(width,(xvals),(yvals))}
    # height is height for all characters
    # gap is gap between characters
    # per character: width is character width
    # per character: (xvals) and (yvals) are the x,y pixel locations from top left
    # iterate over zip(xvals,yvals)
    chars = {
        'height': 7,
        'maxwidth': 5,
        'gap': 1,
        ' ': (2,tuple(),tuple()),
        '!':(1,(0,0,0,0,0,0),(0,1,2,3,4,6)),
        '"':(3,(0,2,0,2),(0,0,1,1)),
        '#':(5,(1,3,0,1,2,3,4,1,3,1,3,0,1,2,3,4,1,3),(0,0,1,1,1,1,1,2,2,3,3,4,4,4,4,4,5,5)),
        '$':(5,(1,2,3,0,2,4,0,2,1,2,3,2,4,0,2,4,1,2,3),(0,0,0,1,1,1,2,2,3,3,3,4,4,5,5,5,6,6,6)),
        '%':(5,(0,1,0,1,4,3,2,1,0,3,4,3,4),(0,0,1,1,1,2,3,4,5,5,5,6,6)),
        '&':(5,(1,2,0,3,0,3,1,2,0,4,0,3,1,2,4),(0,0,1,1,2,2,3,3,4,4,5,5,6,6,6)),
        "'":(1,(0,0),(0,1)),
        '(':(3,(2,1,0,0,0,1,2),(0,1,2,3,4,5,6)),
        ')':(3,(0,1,2,2,2,1,0),(0,1,2,3,4,5,6)),
        '*':(3,(1,0,1,2,1),(0,1,1,1,2)),
        '+':(3,(1,0,1,2,1),(2,3,3,3,4)),
        ',':(1,(0,0),(5,6)),
        '-':(3,(0,1,2),(3,3,3)),
        '.':(1,(0,),(6,)),
        '/':(3,(2,1,1,1,0),(1,2,3,4,5)),
        '0':(5,(1,2,3,0,4,0,4,0,4,0,4,0,4,1,2,3),(0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,6)),
        '1':(3,(1,0,1,1,1,1,1,0,1,2),(0,1,1,2,3,4,5,6,6,6)),
        '2':(5,(1,2,3,0,4,4,3,2,1,0,1,2,3,4),(0,0,0,1,1,2,3,4,5,6,6,6,6,6)),
        '3':(5,(1,2,3,0,4,4,2,3,4,0,4,1,2,3),(0,0,0,1,1,2,3,3,4,5,5,6,6,6)),
        '4':(5,(4,0,4,0,4,0,1,2,3,4,4,4,4),(0,1,1,2,2,3,3,3,3,3,4,5,6)),
        '5':(5,(0,1,2,3,4,0,0,0,1,2,3,4,0,4,1,2,3),(0,0,0,0,0,1,2,3,3,3,3,4,5,5,6,6,6)),
        '6':(5,(1,2,3,0,4,0,0,1,2,3,0,4,0,4,1,2,3),(0,0,0,1,1,2,3,3,3,3,4,4,5,5,6,6,6)),
        '7':(5,(0,1,2,3,4,4,3,2,1,1,1),(0,0,0,0,0,1,2,3,4,5,6)),
        '8':(5,(1,2,3,0,4,0,4,1,2,3,0,4,0,4,1,2,3),(0,0,0,1,1,2,2,3,3,3,4,4,5,5,6,6,6)),
        '9':(5,(1,2,3,0,4,0,4,1,2,3,4,4,0,4,1,2,3),(0,0,0,1,1,2,2,3,3,3,3,4,5,5,6,6,6)),
        ':':(1,(0,0),(2,5)),
        ';':(1,(0,0,0),(2,5,6)),
        '<':(4,(3,2,1,0,1,2,3),(0,1,2,3,4,5,6)),
        '=':(3,(0,1,2,0,1,2),(2,2,2,4,4,4)),
        '>':(4,(0,1,2,3,2,1,0),(0,1,2,3,4,5,6)),
        '?':(5,(1,2,3,0,4,3,2,2,2),(0,0,0,1,1,2,3,4,6)),
        '@':(5,(1,2,3,0,4,0,2,4,0,2,3,0,0,4,1,2,3),(0,0,0,1,1,2,2,2,3,3,3,4,5,5,6,6,6)),
        'A':(4,(1,2,0,3,0,3,0,1,2,3,0,3,0,3,0,3),(0,0,1,1,2,2,3,3,3,3,4,4,5,5,6,6)),
        'B':(4,(0,1,2,0,3,0,3,0,1,2,0,3,0,3,0,1,2),(0,0,0,1,1,2,2,3,3,3,4,4,5,5,6,6,6)),
        'C':(4,(1,2,0,3,0,0,0,0,3,1,2),(0,0,1,1,2,3,4,5,5,6,6)),
        'D':(4,(0,1,2,0,3,0,3,0,3,0,3,0,3,0,1,2),(0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,6)),
        'E':(4,(0,1,2,3,0,0,0,1,2,0,0,0,1,2,3),(0,0,0,0,1,2,3,3,3,4,5,6,6,6,6)),
        'F':(4,(0,1,2,3,0,0,0,1,2,0,0,0),(0,0,0,0,1,2,3,3,3,4,5,6)),
        'G':(4,(1,2,0,3,0,0,2,3,0,3,0,3,1,2,3),(0,0,1,1,2,3,3,3,4,4,5,5,6,6,6)),
        'H':(4,(0,3,0,3,0,3,0,1,2,3,0,3,0,3,0,3),(0,0,1,1,2,2,3,3,3,3,4,4,5,5,6,6)),
        'I':(3,(0,1,2,1,1,1,1,1,0,1,2),(0,0,0,1,2,3,4,5,6,6,6)),
        'J':(4,(2,3,3,3,3,3,0,3,1,2),(0,0,1,2,3,4,5,5,6,6)),
        'K':(4,(0,3,0,2,0,1,0,1,0,2,0,3,0,3),(0,0,1,1,2,2,3,3,4,4,5,5,6,6)),
        'L':(4,(0,0,0,0,0,0,0,1,2,3),(0,1,2,3,4,5,6,6,6,6)),
        'M':(5,(0,4,0,1,3,4,0,2,4,0,4,0,4,0,4,0,4),(0,0,1,1,1,1,2,2,2,3,3,4,4,5,5,6,6)),
        'N':(4,(0,3,0,1,3,0,2,3,0,3,0,3,0,3,0,3),(0,0,1,1,1,2,2,2,3,3,4,4,5,5,6,6)),
        'O':(4,(1,2,0,3,0,3,0,3,0,3,0,3,1,2),(0,0,1,1,2,2,3,3,4,4,5,5,6,6)),
        'P':(4,(0,1,2,0,3,0,3,0,1,2,0,0,0),(0,0,0,1,1,2,2,3,3,3,4,5,6)),
        'Q':(4,(1,2,0,3,0,3,0,3,0,3,0,2,1,3),(0,0,1,1,2,2,3,3,4,4,5,5,6,6)),
        'R':(4,(0,1,2,0,3,0,3,0,1,2,0,2,0,3,0,3),(0,0,0,1,1,2,2,3,3,3,4,4,5,5,6,6)),
        'S':(4,(1,2,0,3,0,1,2,3,0,3,1,2),(0,0,1,1,2,3,3,4,5,5,6,6)),
        'T':(5,(0,1,2,3,4,2,2,2,2,2,2),(0,0,0,0,0,1,2,3,4,5,6)),
        'U':(4,(0,3,0,3,0,3,0,3,0,3,0,3,1,2),(0,0,1,1,2,2,3,3,4,4,5,5,6,6)),
        'V':(5,(0,4,0,4,0,4,0,4,0,4,1,3,2),(0,0,1,1,2,2,3,3,4,4,5,5,6)),
        'W':(5,(0,4,0,4,0,4,0,2,4,0,2,4,0,1,3,4,0,4),(0,0,1,1,2,2,3,3,3,4,4,4,5,5,5,5,6,6)),
        'X':(5,(0,4,0,4,1,3,2,1,3,0,4,0,4),(0,0,1,1,2,2,3,4,4,5,5,6,6)),
        'Y':(5,(0,4,0,4,1,3,2,2,2,2),(0,0,1,1,2,2,3,4,5,6)),
        'Z':(5,(0,1,2,3,4,4,3,2,1,0,0,1,2,3,4),(0,0,0,0,0,1,2,3,4,5,6,6,6,6,6)),
        '[':(3,(0,1,2,0,0,0,0,0,0,1,2),(0,0,0,1,2,3,4,5,6,6,6)),
        '\\':(3,(0,1,1,1,2),(1,2,3,4,5)),
        ']':(3,(0,1,2,2,2,2,2,2,0,1,2),(0,0,0,1,2,3,4,5,6,6,6)),
        '^':(3,(1,0,2),(0,1,1)),
        '_':(3,(0,1,2),(6,6,6)),
        '`':(2,(0,1),(0,1)),
        '{':(3,(2,1,1,0,1,1,2),(0,1,2,3,4,5,6)),
        '|':(1,(0,0,0,0,0,0),(0,1,2,4,5,6)),
        '}':(3,(0,1,1,2,1,1,0),(0,1,2,3,4,5,6)),
        '~':(5,(0,1,2,2,3,4),(2,2,2,3,3,3)),
        }

    # place text
    def place_text(self,text,x,y,center=False,middle=False,color='red',bright=0,write=False):

        # the text origin is from TOP-LEFT
        # default x,y values are TOP-LEFT of text
        # if center, x value is center of text
        # if middle, y value is middle of text

        # fix text
        text = str(text).upper()
        text = ''.join([c for c in text if c in self.chars])

        # have text
        if text:

            # get color
            color = self.get_color(color,bright)

            # char values
            char_height = self.chars['height']
            char_maxwidth = self.chars['maxwidth']
            char_gap = self.chars['gap']

            # middle
            if middle:
                y -= int(char_height//2)

            # centered
            if center:
                tlen = sum((self.chars[c][0] for c in text)) + (len(text)-1)*char_gap
                x -= int(tlen//2)

            # place
            xstop = self.pixelx-1
            ystop = self.pixely-1
            for char in text:
 
                # get char values
                width,xvals,yvals = self.chars[char]

                # skip ahead
                if x + width > 0:

                    # set values
                    for px,py in zip(xvals,yvals):
                        X = x+px
                        Y = y+py
                        if 0 <= X <= xstop and 0 <= Y <= ystop:
                            self.setxy(X,Y,color,cfixed=True,write=False)

                # advance to next x
                x += width + char_gap

                # done
                if x >= xstop:
                    break
            
            # write
            if write:
                self.write()

    def scroll_text(self,text,x1,y1,x2,y2,center=False,middle=False,color='red',bright=0,background='black',bbright=0,pause=40):

        # everything is done locally so that it can scroll fast
        # loop time is about 40ms so any pause below 40 is no pause
        # pause of 50 is a fast scroll

        # fix text
        text = str(text).upper()
        text = ''.join([c for c in text if c in self.chars])

        # have text
        if text:

            # get colors
            color = self.get_color(color,bright)
            background = self.get_color(background,bbright)

            # char values
            char_height = self.chars['height']
            char_maxwidth = self.chars['maxwidth']
            char_gap = self.chars['gap']

            # max limits
            xstop = self.pixelx-1
            ystop = self.pixely-1

            # setxy values
            panpix = 64*self.panelx
            allpix = self.pixels

            # middle
            if middle:
                y1 -= int(char_height//2)
                y2 -= int(char_height//2)

            # centered (keep tlen)
            tlen = sum((self.chars[c][0] for c in text)) + (len(text)-1)*char_gap
            if center:
                x1 -= int(tlen//2)
                x2 -= int(tlen//2)

            # pause
            loop_time = 0

            # follow line
            for x,y in self.line_points(x1,y1,x2,y2):

                # only if some characters can be seen
                if x <= xstop and x + tlen > 0 and y <= ystop and y + char_height > 0:

                    # pause
                    while time.ticks_diff(time.ticks_ms(),loop_time) < pause:
                        time.sleep_ms(1)
                    loop_time = time.ticks_ms()

                    # place text
                    toclear = []
                    for char in text:

                        # get char values
                        width,xvals,yvals = self.chars[char]

                        # or skip ahead
                        if x + width > 0:

                            # set values
                            for px,py in zip(xvals,yvals):
                                X = x+px
                                Y = y+py
                                if 0 <= X <= xstop and 0 <= Y <= ystop:
                                    #local setxy
                                    pixel = panpix * (Y//8) + 64 * (X//8) + 8 * (Y%8) + X%8
                                    if 0 <= pixel <= allpix:
                                        toclear.append((X,Y))
                                        self.array[pixel*3:pixel*3+3] = color

                        # advance to next x
                        x += width + char_gap

                        # done
                        if x >= xstop:
                            break

                    # write
                    neopixel_write(self.p,self.array,1)

                    # clear
                    for X,Y in toclear:
                        #local setxy
                        pixel = panpix * (Y//8) + 64 * (X//8) + 8 * (Y%8) + X%8
                        self.array[pixel*3:pixel*3+3] = background

            # final
            neopixel_write(self.p,self.array,1)

    def scroll(self,text,y=0,color='red',bright=0,background='black',bbright=0,pause=40):

        # normal text scroll, right to left

        # fix text
        text = str(text).upper()
        text = ''.join([c for c in text if c in self.chars])

        # get text len
        tlen = sum((self.chars[c][0] for c in text)) + (len(text)-1)*self.chars['gap']

        x1 = self.pixelx
        x2 = 0 - tlen

        self.scroll_text(text,x1,y,x2,y,False,False,color,bright,background,bbright,pause)

#-----------------------
# end
#-----------------------































