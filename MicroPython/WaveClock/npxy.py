# npxy.py
# Copyright (c) 2017 Clayton Darwin
# claytondarwin.com claytondarwin@gmail.com

# notify
print('LOAD: npxy.py')

#---------------------------------------------------------------
# Imports
#---------------------------------------------------------------

import time
from os       import urandom
from machine  import Pin
from neopixel import NeoPixel

#---------------------------------------------------------------
# Testing
#---------------------------------------------------------------

#---------------------------------------------------------------
# Colors
#---------------------------------------------------------------

# bold color values
# in color-spectrum order
bold_colors = [

    ('blue',(0,0,255)),

    ('deep blue gatoraide',(0,32,255)),

    ('blue gatoraide',(0,127,255)),

    ('cyan',(0,255,255)),

    ('aqua',(0,255,127)),

    ('electric mint',(0,255,32)),

    ('green',(0,255,0)),

    ('electric lime',(32,255,0)),

    ('green yellow',(127,255,0)),

    ('yellow',(255,255,0)),

    ('orange',(255,127,0)),

    ('electric pumpkin',(255,32,0)),
    
    ('red',(255,0,0)),
          
    ('deep pink',(255,0,32)),

    ('pink',(255,0,127)),

    ('magenta',(255,0,255)),

    ('purple',(127,0,255)),

    ('deep purple',(32,0,255)),

          ]

def get_color_name(name,maxvalue=32):

    color = (255,0,0)
    name = name.lower()
    for n,c in bold_colors:
        if n == name:
            color = c
            break
    # scale
    scale = maxvalue/255
    color = tuple([int(round(x*scale,0)) for x in color])

    # done
    return color

def next_color(maxvalue=32):

    colors = [x[1] for x in bold_colors]
    maxplace = len(colors)-1
    place = 0
    scale = maxvalue/255

    while 1:

        color = colors[place]
        yield tuple([int(round(x*scale,0)) for x in color])

        place += 1
        if place >= maxplace:
            place = 0
    
def random_color(maxvalue=32,nowhite=False):

    colors = [x[1] for x in bold_colors]
    if not nowhite:
        colors += [(255,255,255),(0,0,0)]

    # select
    color = colors[randint(len(colors)-1)]

    # scale
    scale = maxvalue/255
    color = tuple([int(round(x*scale,0)) for x in color])

    # done
    return color

#---------------------------------------------------------------
# Random Numbers
#---------------------------------------------------------------

def randint(maximum=255):

    # the random.randint() returns the same value after start
    # this does better at returning mixed values

    return int(ord(urandom(1))*min(256,maximum+1)/256)

#---------------------------------------------------------------
# XY grid for NeoPixels
#---------------------------------------------------------------

class NPXY:

    # This manages a strip of WS2812B chips (neopixels) arranged into
    # a serpentine pattern to represent the 1st quadrant of an XY grid.
    # This allows updates using XY coordinates (it's way easier).

    # This uses the module neopixel.NeoPixel as the buffer and writer.
    # It will set this up for you based on init variables.

    # The entry point of the grid (i.e. the start of the strip) is the
    # lower left corner, which is typically the origin.

    # The strip can be serpentined in two ways, by row or by column.

    # MODE 1: ROWS
    #
    #        -------------------R2---------------------- >END
    #        |
    #        -------------------R1----------------------
    #                                                  |
    # START> -------------------R0----------------------


    # MODE 2: COLUMNS
    #
    #        |---|   |---|   |---|   | >END
    #        |   |   |   |   |   |   |
    #        |   |   |   |   |   |   |
    #        C1  C2  C3  C4  C5  C6  C7
    #        |   |   |   |   |   |   |
    #        |   |   |   |   |   |   |
    # START> |   |---|   |---|   |---|

    # MODE 3: ROWS always left-to-right
    #
    #        -------------------R2---------------------- >END
    #        |                                            
    #        -------------------------------------------
    #                                                  |
    #        -------------------R1----------------------
    #        |                                            
    #        -------------------------------------------
    #                                                  |
    # START> -------------------R0----------------------


    # MODE 4: COLUMNS always bottom-to-top
    # this is the typical 8x8 grid of neopixels you buy
    #
    #        |--|  |--|  |--|  |--|  |--|  |--|  | >END
    #        |  |  |  |  |  |  |  |  |  |  |  |  |
    #        |  |  |  |  |  |  |  |  |  |  |  |  |
    #        C1 |  C2 |  C3 |  C4 |  C5 |  C6 |  C7
    #        |  |  |  |  |  |  |  |  |  |  |  |  |
    #        |  |  |  |  |  |  |  |  |  |  |  |  |
    # START> |  |--|  |--|  |--|  |--|  |--|  |--|

    # Init Variables:

    # pin = The pin number to use for output to the pixel strip.

    # width = The width of the grid in pixels.
    # height = The height of the grid in pixels.
    # The width*height should be the total pixels (length of strip).

    # colors = default 3, the number of color values 3 per pixel.
    # If not 3 or 4, the behavior is undefined at this time.

    # timing = default True, sets the neopixel.NeoPixel timing.

    # mode = default 1, sets the strip serpentine mode (see above).

    # Use these if you DO NOT want the lower left pixel to be (1,1).
    # xoffset = default -1, the x offset of grid origin from lower left corner
    # yoffset = default -1, the y offset of grid origin from lower left corner

    # Functions:

    # write() = write grid buffer to pin (out to strip)

    # fill(*color) = fill grid with this color

    # off() = fill grid with zeros AND WRITE

    # clear() = fill grid with zeros

    # setp(x,y,*color) = set grid pixel (x,y) to color

    # getp(x,y,*ignore) = get color of grid pixel (x,y)

    # load_font(fontfile,limit_to) = load the font file, limit to chars in string

    # fix_text(text,smash=True,strip=True,upper=True)
    #   fix/clean a string of text for printing (usually not called directly)
    #   smash = compress whitespace
    #   strip = text.strip()
    #   upper = text.upper() (required for default font)
    
    # place_text(text,color,xshift=0,yshift=0,smash=True,strip=True,upper=True,fixed=False)
    #   place text offset (xshift and yshift) from the lower-left corner
    #   color is a color tuple for text
    #   smash = compress whitespace
    #   strip = text.strip()
    #   upper = text.upper() (required for default font)
    #   fixed = don't use self.fix_text (already done)
    
    # center_text(text,color,smash=True,strip=True,upper=True)
    #   center text in grid as much as possible
    #   color is a color tuple for text
    #   smash = compress whitespace
    #   strip = text.strip()
    #   upper = text.upper() (required for default font)
    
    # scroll_text(text,color,background=None,  smash=True,strip=True,upper=True)
    #   scroll text in grid from right to left
    #   color is a color tuple for text
    #   background is a background color to fill (a color tuple)
    #   smash = compress whitespace
    #   strip = text.strip()
    #   upper = text.upper() (required for default font)

    # test_strip(loops) = run red, green, and blue sequences up strip
    #                     do this "loop" times (set loop=None for forever)

    # random_flash(loops,fast) = random flash strip pixels random colors
    #                            do this "loop" times (set loop=None for forever)
    #                            if "fast"=True, do it as fast as you can
    #                            otherwise do random pauses

    #-----------------------------------------------------------
    # init
    #-----------------------------------------------------------

    def __init__(self,pin,width,height,colors=3,timing=True,mode=1,xoffset=-1,yoffset=-1):

        # save input
        self.width = width
        self.height = height
        self.colors = colors
        self.xoffset = xoffset
        self.yoffset = yoffset

        # set mode functions
        if mode not in (1,2,3,4):
            mode = 1
        if mode == 1:
            self.setp   = self.setp_rows
            self.getp   = self.getp_rows
            self.setpzf = self.setp_rows_zf
        elif mode == 2:
            self.setp   = self.setp_cols
            self.getp   = self.getp_cols
            self.setpzf = self.setp_cols_zf
        elif mode == 3:
            self.setp   = self.setp_rows_z
            self.getp   = self.getp_rows_z
            self.setpzf = self.setp_rows_z_zf
        elif mode == 4:
            self.setp   = self.setp_cols_z
            self.getp   = self.getp_cols_z
            self.setpzf = self.setp_cols_z_zf

        # set up pin
        self.pin = Pin(pin,Pin.OUT)
        self.pin.value(0)

        # set up neopixel class (acts as buffer)
        self.pixels = width*height
        if colors == 4:
            self.np = NeoPixel(self.pin,self.pixels,timing=timing,bpp=4)
        else:
            self.np = NeoPixel(self.pin,self.pixels,timing=timing)
        self.off()

    #-----------------------------------------------------------
    # non-XY functions
    #-----------------------------------------------------------

    def write(self):

        self.np.write()

    def off(self):

        self.clear(True)

    def clear(self,send=False):

        color = (0,)*self.colors

        for x in range(self.pixels):
            self.np[x] = color

        if send:
            self.np.write()

    def fill(self,color):

        # this is faster than using self.np.fill

        color = (color+(0,)*self.colors)[:self.colors]

        for x in range(self.pixels):
            self.np[x] = color

    #-----------------------------------------------------------
    # XY functions
    #-----------------------------------------------------------

    # these are not used directly (use setp and getp)

    def row_pixel(self,x,y):
        
        y += self.yoffset
        x += self.xoffset

        if 0 <= y < self.height and 0 <= x < self.width:

            # even row = LR
            if y%2==0:
                return y*self.width + x

            # odd row = RL
            else:
                return y*self.width + self.width - 1 - x

        return None

    def row_pixel_z(self,x,y):
        
        y += self.yoffset
        x += self.xoffset

        if 0 <= y < self.height and 0 <= x < self.width:

            return y*self.width + x

        return None

    def col_pixel(self,x,y):
        
        y += self.yoffset
        x += self.xoffset

        if 0 <= y < self.height and 0 <= x < self.width:

            # even col = BT
            if x%2==0:
                return x*self.height + y

            # odd col = TB
            else:
                return x*self.height + self.height - 1 - y

        return None

    def col_pixel_z(self,x,y):
        
        y += self.yoffset
        x += self.xoffset

        if 0 <= y < self.height and 0 <= x < self.width:

            return x*self.height + y

        return None

    def setp_rows(self,x,y,*color):

        pixel = self.row_pixel(x,y)

        if pixel != None:
            self.np[pixel] = (color+(0,)*self.colors)[:self.colors]

    def setp_rows_z(self,x,y,*color):

        pixel = self.row_pixel_z(x,y)

        if pixel != None:
            self.np[pixel] = (color+(0,)*self.colors)[:self.colors]

    def setp_cols(self,x,y,*color):

        pixel = self.col_pixel(x,y)

        if pixel != None:
            self.np[pixel] = (color+(0,)*self.colors)[:self.colors]
   
    def setp_cols_z(self,x,y,*color):

        pixel = self.col_pixel_z(x,y)

        if pixel != None:
            self.np[pixel] = (color+(0,)*self.colors)[:self.colors]
   
    def getp_rows(self,x,y,*rest):

        pixel = self.row_pixel(x,y)

        if pixel != None:
            return self.np[pixel]

    def getp_rows_z(self,x,y,*rest):

        pixel = self.row_pixel_z(x,y)

        if pixel != None:
            return self.np[pixel]

    def getp_cols(self,x,y,*rest):

        pixel = self.col_pixel(x,y)

        if pixel != None:
            return self.np[pixel]

    def getp_cols_z(self,x,y,*rest):

        pixel = self.col_pixel_z(x,y)

        if pixel != None:
            return self.np[pixel]

    def setp_rows_zf(self,x,y,color):

        # index from 0, no checks (fast)

        if y%2==0:
            self.np[y*self.width+x] = color

        else:
            self.np[y*self.width+self.width-1-x] = color

    def setp_rows_z_zf(self,x,y,color):

        # index from 0, no checks (fast)

        self.np[y*self.width+x] = color

    def setp_cols_zf(self,x,y,color):

        # index from 0, no checks (fast)

        if y%2==0:
            self.np[x*self.height+y] = color

        else:
            self.np[x*self.height+self.height-1-y] = color

    def setp_cols_z_zf(self,x,y,color):

        # index from 0, no checks (fast)

        self.np[x*self.height+y] = color

    #-----------------------------------------------------------
    # text display functions
    #-----------------------------------------------------------

    # this is the default font
    # this was generated with npxy_make_font.py
    font  = ['  X  XXXX  XX XXX XXXXX    XXXX  XXXX XX X  XXXXXX   XX  X XX X    X XX  X XX   X   XX   X  X   XX   X  X  XXXX XXX XXXXXXXX XXX     X XXX  XXX  X    XXX  XXX         XXXXXX   X XX        X XXX       XXX    XX    XX X XX XX   XX  XXX     XX  X         X          X       X  ', '  X  XX  XX  XX  XX   X   X  XX  X X X  XX  XX   X   XX  XX  XX   X X X  XX  X  X  X  X X X XX XXX   X  X  X   X   X X  X   X   X    XX   XX   X X   X   XX   X        X    X  XX X X        X   X X X X X XX  XX   X  X XXX XXX X  X        X  X XX     XXXXX   XX   XXXXX       ', '  X  XX  XX   X  XX   X   X  XX  X X    XX X X   X   XX  XX  XX   X  XX X    X  X  X  XX   XX X X X X   X   X  X   X X   X      X    X    XX   X X   X   X    X     XXXX    X X      X      XX    XXXXX  X X X      X   XXXX XXXX    X    X  X  X X     X     X X  X X     X   X  ', '  XXXXXXX X   X  XXXX XXX X XXXXXX X    XXX  X   X   XX  XX  XXXX X  XXXX  XX   X  X  XX   XX   X  X    X    X X   X X    X   XX XXXXXXXXX XXXX   X   XXX  XXXX  XXX   X    X X      X   XXXXX XX  X X  XXX   X      XX     X   X    X   XXXXX  XX     X       XX  XX       X  X  ', '  X  XX  XX   X  XX   X   X   X  X X    XXX  X   X X XX XXX  XX  XX  XX  XX     X  X  XX   XX   X X X  X X    XX   X X     X    XX   XX    X       X X   XX   X     XXXX    X X X    X XXX  XX X X X X X X     X    X  X XXX XXXX    X    X  X  X XX    X     X X  X X     X    X ', '  X  XX  XX  XX  XX   X   X  XX  X X    XX X X   XX XXXX XX  XX  XX  XX  XX  X  X  X  XX   XX   XX   XX   X   XX   XXX X   XX   XX   XX    X   X    XX   XX   X X      X    XX   X    X     XX   XXXXXXX X XXX  XX XX  X XXX XXX X  X        X  X X X X  XXXXX   XX   XXXXX  X   X', '   XX XXX  XX XXX XXXXXXXX XX X  XXXX  XXX  XX   X   XX  X XX XXX  XX XXX  XX XXXXXX  XX   XX   XX   XX   XXXXX XXX  X  XXX  XXX     XXXXXX XXX XXXXX XXX  XXX X       XXXXXX    X          X XXX  X X  XXX XX    X  XX   XX XX   XX          XX  X X X   X              X    XXX ']
    chars = {'height': 7, ' ': (' ', 2, 0), 'A': ('A', 4, 2), 'B': ('B', 4, 6), 'C': ('C', 4, 10), 'D': ('D', 4, 14), 'E': ('E', 4, 18), 'F': ('F', 4, 22), 'G': ('G', 4, 26), 'H': ('H', 4, 30), 'I': ('I', 3, 34), 'J': ('J', 4, 37), 'K': ('K', 4, 41), 'L': ('L', 4, 45), 'M': ('M', 5, 49), 'N': ('N', 4, 54), 'O': ('O', 4, 58), 'P': ('P', 4, 62), 'Q': ('Q', 4, 66), 'R': ('R', 4, 70), 'S': ('S', 4, 74), 'T': ('T', 5, 78), 'U': ('U', 4, 83), 'V': ('V', 5, 87), 'W': ('W', 5, 92), 'X': ('X', 5, 97), 'Y': ('Y', 5, 102), 'Z': ('Z', 4, 107), '0': ('0', 5, 111), '1': ('1', 3, 116), '2': ('2', 5, 119), '3': ('3', 5, 124), '4': ('4', 5, 129), '5': ('5', 5, 134), '6': ('6', 5, 139), '7': ('7', 5, 144), '8': ('8', 5, 149), '9': ('9', 5, 154), '`': ('`', 2, 159), '-': ('-', 3, 161), '=': ('=', 3, 164), '[': ('[', 3, 167), ']': (']', 3, 170), '\\': ('\\', 3, 173), ';': (';', 1, 176), "'": ("'", 1, 177), ',': (',', 1, 178), '.': ('.', 1, 179), '/': ('/', 3, 180), '~': ('~', 5, 183), '!': ('!', 1, 188), '@': ('@', 5, 189), '#': ('#', 5, 194), '$': ('$', 5, 199), '%': ('%', 5, 204), '^': ('^', 3, 209), '&': ('&', 5, 212), '*': ('*', 7, 217), '(': ('(', 3, 224), ')': (')', 3, 227), '_': ('_', 3, 230), '+': ('+', 3, 233), '{': ('{', 3, 236), '}': ('}', 3, 239), '|': ('|', 1, 242), ':': (':', 1, 243), '"': ('"', 3, 244), '<': ('<', 11, 247), '>': ('>', 11, 258), '?': ('?', 5, 269)} #

    def fix_text(self,text,smash=True,strip=True,upper=True):

        # upper case
        if upper:
            text = text.upper()

        # replace unknown characters
        text = ''.join([self.chars.get(c,(' ',0,0))[0] for c in text])

        # handle whitespace
        if smash:
            text = ' '.join(text.split())
        else:
            text = text.replace('\n',' ')
            text = text.replace('\t','    ')
            if strip:
                text = text.strip()

        return text

    def place_text(self,text,color,xshift=0,yshift=0,smash=True,strip=True,upper=True,fixed=False):

        if not fixed:
            text = self.fix_text(text,smash,strip,upper)

        if text:
            xindex = 0
            char_height = self.chars['height']
            for c in text:
                c2,cwidth,cindex = self.chars[c]
                for x in range(cwidth):
                    cX = cindex + x
                    tX = xindex + xshift - self.xoffset
                    for cY in range(char_height-1,-1,-1):
                        if self.font[cY][cX] == 'X':
                            tY = cY + yshift - self.yoffset
                            self.setp(tX,tY,*color)
                    xindex += 1
                xindex += 1
                if xindex + xshift - self.xoffset >= self.width:
                    break

    def center_text(self,text,color,smash=True,strip=True,upper=True,nofix=False):

        # DO NOT use offsets (applied in place_text() and setp())

        if not nofix:
            text = self.fix_text(text,smash,strip,upper)

        if text:

            if self.chars['height'] >= self.height:
                yshift = 0
            else:
                yshift = int( (self.height - self.chars['height']) // 2 )

            tlen = sum([self.chars[c][1] for c in text]) + len(text) - 1
            if tlen >= self.width:
                xshift = 0
            else:               
                xshift = int( (self.width - tlen) // 2 )

            self.place_text(text,color,xshift,yshift,fixed=True)

    def scroll_text(self,text,color,background=None,smash=True,strip=True,upper=True,interrupt=None):

        text = self.fix_text(text,smash,strip,upper)

        if text:

            # y shift
            if self.chars['height'] >= self.height:
                yshift = 0
            else:
                yshift = int( (self.height - self.chars['height']) // 2 )

            # make block text from font
            lines = []
            char_height = self.chars['height']
            for y in range(char_height-1,-1,-1):
                lines.append(' '*self.width)
            for c in text:
                c2,cwidth,cindex = self.chars[c]
                for y in range(char_height-1,-1,-1):
                    lines[y] += self.font[y][cindex:cindex+cwidth]
                for y in range(char_height-1,-1,-1):
                    lines[y] += ' '           
            for y in range(char_height-1,-1,-1):
                lines[y] += ' '*self.width

            # it's too slow to do a background fill each time
            # do an intial fill (clear)
            # place text using text color
            # write to pixels
            # place text using background color (erase)

            # this needs more work

            # initial background color
            if not background:
                background = (0,)*self.colors
                self.clear()
            else:
                self.fill(*background)

            # iter through font lines, send self.width cols
            lastloop = 0
            for x1 in range(0,len(lines[0])-self.width,1):

                # wait
                while time.ticks_ms()/1000 - lastloop < 0.1:
                    time.sleep(0.001)
                lastloop = time.ticks_ms()/1000

                # set text
                for x2 in range(self.width):
                    for y in range(char_height-1,-1,-1):
                        if lines[y][x1+x2] == 'X':
                            ty = y + yshift
                            tx = x2
                            self.setpzf(tx,ty,color)

                # write
                self.write()

                # erase
                for x2 in range(self.width):
                    for y in range(char_height-1,-1,-1):
                        if lines[y][x1+x2] == 'X':
                            ty = y + yshift
                            tx = x2
                            self.setpzf(tx,ty,background)

                # interrupt
                if interrupt and interrupt['flag']:
                    self.off()
                    break

    def flash_chars(self,text,color,ontime=0.25,offtime=0.25,smash=True,strip=True,upper=True,interrupt=None):

        text = self.fix_text(text,smash,strip,upper)

        for char in text:

            self.flash_char(char,color,ontime=0.25,offtime=0.25,nofix=True)
            
            # interrupt
            if interrupt and interrupt['flag']:
                self.off()
                break

    def flash_char(self,char,color,ontime=0.25,offtime=0.25,nofix=False):

        char = char[0]

        if not nofix:
            char = self.fix_text(char)

        self.center_text(char,color,nofix=True)
        self.write()
        time.sleep(ontime)

        self.off()
        # self.off calls self.write()
        time.sleep(offtime)

    #-----------------------------------------------------------
    # testing
    #-----------------------------------------------------------

    def test_strip(self,maxvalue=32,loops=None,sleep=0.01,interrupt=None):

        self.off()

        try:

            loopcount = 0
            for color in next_color(maxvalue):
                off = (0,0,0)
                if self.colors == 4:
                    color += (0,)
                    off = (0,0,0,0)
                self.clear()
                for x in range(self.pixels):
                    if x == 0:
                        self.np[self.pixels-1] = off
                    else:
                        self.np[x-1] = off
                    self.np[x] = color
                    self.write()
                    time.sleep(sleep)
                loopcount += 1
                if loops and loopcount >= loops:
                    break

                # interrupt
                if interrupt and interrupt['flag']:
                    self.off()
                    break

        except KeyboardInterrupt:
            pass

        finally:
            self.off()

    def random_flash(self,maxvalue=64,loops=None,fast=False,interrupt=None):

        self.off()

        try:

            loopcount = 0
            while 1:
                
                pixel = randint(self.pixels-1)

                color = random_color(maxvalue)
                off   = (0,0,0)
                if self.colors == 4:
                    color += (0,)
                    off = (0,0,0,0)

                self.np[pixel] = color
                self.np.write()

                if not fast:
                    time.sleep(randint(25)/100)
                else:
                    time.sleep(0.05)

                self.np[pixel] = off
                self.np.write()

                if not fast:
                    time.sleep(randint(50)/100)

                loopcount += 1
                if loops and loopcount >= loops:
                    break

                # interrupt
                if interrupt and interrupt['flag']:
                    self.off()
                    break
        
        except KeyboardInterrupt:
            pass

        finally:
            self.off()

    #-----------------------------------------------------------
    # end of NPXY class
    #-----------------------------------------------------------
