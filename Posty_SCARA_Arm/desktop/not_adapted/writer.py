# The Python Pins Project - www.PyPins.com
# Copyright (c) 2016 Clayton Darwin
# Module:   writer.py
# By:       Clayton Darwin (claytondarwin@gmail.com).
# Language: Python 3.4
# System:   Linux (Debian64)
# Started:  20151215
# Updated:  20160502

#-----------------------------------------------
# Source 
#-----------------------------------------------

#-----------------------------------------------
# Dependencies
#-----------------------------------------------

# This class will not work without a fully set up STO.

#-----------------------------------------------
# Notes
#-----------------------------------------------

# This class provides some basic fixed-width font functions for a simple plotter.
# The function data is passed to the appropriate function in the stepper motor object (i.e. the xyz object).
# This only works using distances, i.e. heights and widths are distances, not steps.

# NOTE: This class will not work without a fully set up xyz opject.
# The xyz opject must have a NibbleCom Object defined (i.e. NCO, see nibblecom.py).
# The xyz opject must have the named X,Y,Z motors defined in xyz.smo.motors.

#-----------------------------------------------
# Imports
#-----------------------------------------------

import sys

#-----------------------------------------------
# Class: Plotter Fonts
#-----------------------------------------------

class Writer:

    # ------------------------------------------
    # Init
    # ------------------------------------------

    def __init__(self,xyz,X=None,Y=None,Z=None):

        # set stepper motor object
        self.xyz = xyz

        # font
        self.font = 'basic1'

        # left-right alignment from start point
        # 'c' = start point is center of text
        # 'r' = start point is right of text
        # 'l' = start point is left of text
        self.align = 'l'

        # vertical alignment from start point
        # 'm' = start point is middle of text
        # 't' = start point is top of text
        # 'b' = start point is bottom of text
        self.valign = 't'

        # the height of the font (required)
        self.height = None

        # maximum width (drop characters until width <= to this width)
        self.maxwidth = 0 # 0 means don't scale

        # it is better to re-define the up and down functions
        # up down value for Z
        self.updown = None
        self.isup = True # sequence must start in up

    # ------------------------------------------
    # Functions
    # ------------------------------------------

    # this should be re-defined by the user
    def up(self,):
        if not self.isup:
            self.xyz.move('z',self.updown)
            self.isup = True
        print('UP');sys.stdout.flush()

    # this should be re-defined by the user
    def down(self,):
        if self.isup:
            self.xyz.move('z',-self.updown)
            self.isup = False
        print('DOWN');sys.stdout.flush()

    def write(self,text,height=None,maxwidth=None,font=None,csep=None,lsep=None,align=None,valign=None):

        # set height
        if height == None or type(height) not in (int,float):
            if type(self.height) in (int,float) and self.height > 0:
                height = self.height
            else:
                ValueError('No height specified.')

        # set max width
        if maxwidth == None or type(maxwidth) not in (int,float):
            if type(self.maxwidth) in (int,float):
                maxwidth = self.maxwidth
            else:
                maxwidth = 0

        # check font
        if (not font) or (font not in self.fonts):
            if self.font in self.fonts:
                font = self.font
            else:
                font = 'basic1'

        # set sep values
        if csep == None or type(csep) not in (int,float):
            csep = self.fonts[self.font]['csep']
        if lsep == None or type(lsep) not in (int,float):
            lsep = self.fonts[self.font]['lsep']

        # set alignment
        if (not align) or align not in ('c','r','l'):
            if self.align in ('c','r','l'):
                align = self.align
            else:
                align = 'l'
        if (not valign) or valign not in ('m','t','b'):
            if self.valign in ('m','t','b'):
                valign = self.valign
            else:
                valign = 't'

        # scale values
        fheight = self.fonts[font]['height']
        fwidth  = self.fonts[font]['width']
        scale = height/fheight
        width = fwidth*scale
        csepwidth = csep*scale
        lsepheight = lsep*scale
        maxchars = int((maxwidth+csepwidth)//(width+csepwidth))
        print('height',height)
        print('width',width)
        print('csep',csepwidth)
        print('maxwidth',maxwidth)
        print('maxchars',maxchars)

        # break and fix lines (preserve whitespace as much as possible)
        lines = []
        for line in text.split('\n'):            
            line = ''.join([self.fonts[font]['trans'].get(c,' ') for c in line])
            while maxwidth and (len(line) > maxchars):
                print('line',line)
                diff = len(line) - maxchars
                print('diff',diff)
                if '  ' in line: # start dropping multi spaces
                    line = line.replace('  ',' ',diff)
                elif ' ' in line: # then drop spaces
                    line = line.replace(' ','',diff)
                else: # then truncate
                    line = line[:maxchars]
            if align == 'c':
                line = line.center(maxchars)
            elif align == 'r':
                line = line.rjust(maxchars)
            else:
                line = line.ljust(maxchars)
            truelen = len(line)*(width+csepwidth) - csepwidth
            lines.append((line,truelen))
            print([line,len(line),truelen])

        # start in up position
        self.up()
        
        # move startpoint to top left of block
        maxlen = max(x[1] for x in lines)
        if align == 'r':
            self.xyz.move('x',-maxlen)
        elif align == 'c':
            self.xyz.move('x',-maxlen/2)
        blockheight = len(lines)*(height+lsepheight) - lsepheight
        if valign == 'b':
            self.xyz.move('y',blockheight)
        elif valign == 'm':
            self.xyz.move('y',blockheight/2)

        # drop down to bottom left of first line
        # fonts start at bottom left
        self.xyz.move('y',-(height+lsepheight))

        # iterate
        while lines:

            # save start position
            xstart,ystart,zstart = self.xyz.where()

            # get line
            text,ll = lines.pop(0)

            # check
            if text.strip():

                text = '\t'.join(list(text))
                for c in text:
                    if c == '\t':
                        self.xyz.move('x',csepwidth)
                    else:
                        for x,y,z,r in self.fonts[font]['chars'][c]:
                            if z: # up down move
                                if z > 0:
                                    self.up()
                                else:
                                    self.down()
                            elif r: # arc move
                                self.xyz.arcmove(x*scale,y*scale,radius=abs(r)*scale,rotation=r)
                            elif x and not y: # linear x
                                self.xyz.move('x',x*scale)
                            elif y and not x: # linear y
                                self.xyz.move('y',y*scale)
                            else: # ray move
                                self.xyz.raymove(x*scale,y*scale)

            # move to bottom left of next line
            if lines:
                self.xyz.moveto('x',xstart)
                self.xyz.move('y',-(height+lsepheight))

        # leave plotter where if ends

        # end in up position
        self.up()

    # ------------------------------------------
    # Fonts
    # ------------------------------------------

    # the trans is used to translate characters
    # characters not in the trans are not used
    # the height and width are the base values used to scale the characters
    # the csep value is the separation between characters (relative to the height/width)
    # the lsep value is the separation between lines (relative to the height/width)
    # the chars coordinate tuples each represent a move to a new position
    # the chars coordinates are relative moves from the current location
    # all chars start in the bottom left  corner in UP postion
    # all chars end   in the bottom right corner in UP position
    # the chars coordinate values are (x,y,z,r)
    # giving r indicates an arc radius to the new (x,y)
    # a negative value moves clockwise, a positive moves clockwise
    # arc moves cannot be more than 180 degrees (use multiple arcs)
    # giving z as 1 indicates a pen up (as defined by the updown value)
    # giving z as -1 indicates a pen down (as defined by the updown value)
    # giving z as 0 is no change

    fonts = {'basic1':{'trans':dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,?!- ^~_',
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!- ^~ ')),
                       'height':6,
                       'width':4,
                       'csep':1,
                       'lsep':1,
                       'chars':{'A':((0, 0, -1, 0),
                                     (2, 6, 0, 0),
                                     (2, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-3, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                      ),
                                'B':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (2, 0, 0, 0),
                                     (0, -3, 0, -1.5),
                                     (-2, 0, 0, 0),
                                     (2.5, 0, 0, 0),
                                     (0, -3, 0, -1.5),
                                     (-2.5, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, 0, 0, 0),
                                      ),
                                'C':((4, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (-4, 0, 0, -2),
                                     (0, 2, 0, 0),
                                     (4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (0, -4, 0, 0),
                                      ),
                                'D':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (2, 0, 0, 0),
                                     (2, -2, 0, -2),
                                     (0, -2, 0, 0),
                                     (-2, -2, 0, -2),
                                     (-2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, 0, 0, 0),
                                      ),
                                'E':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (-2, -3, 0, 0),
                                     (0, 0, -1, 0),
                                     (-2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -3, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'F':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (-2, -3, 0, 0),
                                     (0, 0, -1, 0),
                                     (-2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, -3, 0, 0),
                                      ),
                                'G':((2, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, -1, 0, 0),
                                     (-4, 0, 0, -2),
                                     (0, 2, 0, 0),
                                     (4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (0, -4, 0, 0),
                                      ),
                                'H':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-4, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -3, 0, 0),
                                      ),
                                'I':((1, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (-1, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-1, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, 0, 0, 0),
                                      ),
                                'J':((1, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (3, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (-1, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, -4.5, 0, 0),
                                     (-3, 0, 0, -1.5),
                                     (0, 0.5, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, -2, 0, 0),
                                      ),
                                'K':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (-4, -4, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, 1, 0, 0),
                                     (0, 0, -1, 0),
                                     (3, -3, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'L':((0, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, -6, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'M':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (2, -3, 0, 0),
                                     (2, 3, 0, 0),
                                     (0, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'N':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (4, -6, 0, 0),
                                     (0, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'O':((0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 2, 0, 0),
                                     (4, 0, 0, -2),
                                     (0, -2, 0, 0),
                                     (-4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (4, -2, 0, 0),
                                      ),
                                'P':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (2.5, 0, 0, 0),
                                     (0, -3, 0, -1.5),
                                     (-2.5, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (4, -3, 0, 0),
                                      ),
                                'Q':((0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 2, 0, 0),
                                     (4, 0, 0, -2),
                                     (0, -2, 0, 0),
                                     (-4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, -2, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'R':((0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (2.5, 0, 0, 0),
                                     (0, -3, 0, -1.5),
                                     (-2.5, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (2.5, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (1.5, -3, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'S':((0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, 2),
                                     (-2, 1, 0, 2),
                                     (-2, 1, 0, -2),
                                     (4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (0, -4, 0, 0),
                                      ),
                                'T':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'U':((0, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, -4, 0, 0),
                                     (4, 0, 0, 2),
                                     (0, 4, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'V':((0, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, -6, 0, 0),
                                     (2, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'W':((0, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (1, -6, 0, 0),
                                     (1, 3, 0, 0),
                                     (1, -3, 0, 0),
                                     (1, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'X':((0, 0, -1, 0),
                                     (4, 6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-4, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                'Y':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 3, 0, 0),
                                     (-2, 3, 0, 0),
                                     (0, 0, 1, 0),
                                     (2, -3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 3, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                'Z':((0, 6, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, 0),
                                     (-4, -6, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                '0':((0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 2, 0, 0),
                                     (4, 0, 0, -2),
                                     (0, -2, 0, 0),
                                     (-4, 0, 0, -2),
                                     (0, 0, 1, 0),
                                     (1, 1, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                      ),
                                '1':((1, 5, 0, 0),
                                     (0, 0, -1, 0),
                                     (1, 1, 0, 0),
                                     (0, -6, 0, 0),
                                     (0, 0, 1, 0),
                                     (-1, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, 0, 0, 0),
                                      ),
                                '2':((0, 4, 0, 0),
                                     (0, 0, -1, 0),
                                     (4, 0, 0, -2),
                                     (-4, -4, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, 0, 0, 0),
                                      ),
                                '3':((0, 4.5, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 1.5, 0, -2),
                                     (2, -1.5, 0, -2),
                                     (-2, -1.5, 0, -2),
                                     (2, -1.5, 0, -2),
                                     (-2, -1.5, 0, -2),
                                     (-2, 1.5, 0, -2),
                                     (0, 0, 1, 0),
                                     (4, -1.5, 0, 0),
                                      ),
                                '4':((3, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 6, 0, 0),
                                     (-3, -4, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -2, 0, 0),
                                      ),
                                '5':((0, 1, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, -1, 0, 2),
                                     (0, 4, 0, 2),
                                     (-2, -1, 0, 2),
                                     (0, 3, 0, 0),
                                     (4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                '6':((0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 1, 0, -2),
                                     (2, -1.5, 0, -2),
                                     (-2, -1.5, 0, -2),
                                     (-2, 2, 0, -2),
                                     (4, 4, 0, -4),
                                     (0, 0, 1, 0),
                                     (0, -6, 0, 0),
                                      ),
                                '7':((1, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (3, 6, 0, 0),
                                     (-4, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                      ),
                                '8':((2, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (-2, 1.5, 0, -2),
                                     (2, 1.5, 0, -2),
                                     (2, -1.5, 0, -2),
                                     (-2, -1.5, 0, -2),
                                     (2, -1.5, 0, -2),
                                     (-2, -1.5, 0, -2),
                                     (-2, 1.5, 0, -2),
                                     (2, 1.5, 0, -2),
                                     (0, 0, 1, 0),
                                     (2, -3, 0, 0),
                                      ),
                                '9':((0, 0, -1, 0),
                                     (4, 4, 0, 4),
                                     (-2, 2, 0, 2),
                                     (-2, -1.5, 0, 2),
                                     (2, -2, 0, 2),
                                     (2, 1, 0, 2),
                                     (0, 0, 1, 0),
                                     (0, -4, 0, 0),
                                      ),
                                ' ':((4, 0, 0, 0),
                                      ),
                                '.':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 1, 0, 0.5),
                                     (0, -1, 0, 0.5),
                                     (0, 0, 1, 0),
                                     (2, 0, 0, 0),
                                      ),
                                ',':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0.5, 0.5, 0, 0),
                                     (-1, -1, 0, 0),
                                     (0.5, 0.5, 0, 0),
                                     (0, 0, 1, 0),
                                     (2, 0, 0, 0),
                                      ),
                                '?':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 1, 0, 0.5),
                                     (0, -1, 0, 0.5),
                                     (0, 0, 1, 0),
                                     (0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 1, 0, 0),
                                     (2, 1.5, 0, 2),
                                     (-2, 1.5, 0, 2),
                                     (-2, -2, 0, 2),
                                     (0, 0, 1, 0),
                                     (4, -4, 0, 0),
                                      ),
                                '!':((2, 0, 0, 0),
                                     (0, 0, -1, 0),
                                     (0, 1, 0, 0.5),
                                     (0, -1, 0, 0.5),
                                     (0, 0, 1, 0),
                                     (0, 2, 0, 0),
                                     (0, 0, -1, 0),
                                     (-0.5, 3.5, 0, 0),
                                     (1, 0, 0, 0.5),
                                     (-0.5, -3.5, 0, 0),
                                     (0, 0, 1, 0),
                                     (2, -2, 0, 0),
                                      ),
                                '-':((1, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                      ),
                                # darth vader
                                '^':(

                                     # outline + eye outline
                                     ( 0   , 2   , 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 4   , 0   , 0, 3.0  ),
                                     (-0.5 , 2   , 0, 0    ),
                                     ( 0   , 0.5 , 0, 0    ),
                                     (-3   , 0   , 0, 1.5  ),
                                     ( 0   ,-0.5 , 0, 0    ),
                                     (-0.5 ,-2   , 0, 0    ),
                                     ( 0.75, 2   , 0, 0    ),
                                     ( 1.25, 0   , 0,-0.625),
                                     ( 1.25, 0   , 0,-0.625),
                                     ( 0.75,-2   , 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),

                                     # mouth triangle
                                     (-1   ,-0.5 , 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     (-1   , 1.5 , 0, 0    ),
                                     (-1   ,-1.5 , 0, 0    ),
                                     ( 2   , 0   , 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),
                                     (-0.5 , 0.75, 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 0   ,-0.75, 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),
                                     (-0.5 , 0   , 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 0   , 1.5 , 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),
                                     (-0.5 ,-0.75, 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 0   ,-0.75, 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),

                                     # beard
                                     ( 0   ,-0.5 , 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 0.5 ,-0.5 , 0, 0    ),
                                     ( 0.5 , 0.5 , 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),

                                     # eyes
                                     (-1.75, 2.25, 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 1   , 0   , 0, 0    ),
                                     ( 0.25, 0.25, 0, 0    ),
                                     ( 0.25,-0.25, 0, 0    ),
                                     ( 1   , 0   , 0, 0    ),
                                     (-0.25, 0.75, 0, 0    ),
                                     (-0.75, 0   , 0, 0.375),
                                     (-0.25,-0.5 , 0, 0    ),
                                     (-0.25, 0.5 , 0, 0    ),
                                     (-0.75, 0   , 0, 0.375),
                                     (-0.25,-0.75, 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),

                                     # center helmet line
                                     ( 1.25, 1.25, 0, 0    ),
                                     ( 0   , 0   ,-1, 0    ),
                                     ( 0   , 1.5 , 0, 0    ),
                                     ( 0   , 0   , 1, 0    ),

                                     # go to end point
                                     ( 2   ,-5.5 , 0, 0    ),

                                     ),
                                # heart
                                '~':((1, 3, 0, 0),
                                     (0, 0, -1, 0),
                                     (2, 0, 0, 0),
                                     (0, 0, 1, 0),
                                     (1, -3, 0, 0),
                                      ),
                                }, # end of 'chars'
                       }, # end of 'basic1'
             } # end of fonts

# old font data and conversion

##    fonts = [{'name':'basic1',
##              'trans':dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,?!-',
##                               'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,?!-')),
##              'height':6,
##              'width':4,
##              'chars':{'A':'''g0 zd
##                              g1 x2 y6
##                              g1 x2 y-6
##                              g0 zu
##                              g0 x-3 y3
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y-3 '''.split('\n'),
##                       'B':'''g0 zd
##                              g1 y6
##                              g1 x2
##                              g2 y-3 r1.5
##                              g1 x-2
##                              g1 x2.5
##                              g2 y-3 r1.5
##                              g1 x-2.5
##                              g0 zu
##                              g0 x4 y0 '''.split('\n'),
##                       'C':'''g0 x4 y2
##                              g0 zd
##                              g2 x-4 r2
##                              g1 y2
##                              g2 x4 r2
##                              g0 zu
##                              g0 x0 y-4 '''.split('\n'),
##                       'D':'''g0 zd
##                              g1 y6
##                              g1 x2
##                              g2 x2 y-2 r2
##                              g1 y-2
##                              g2 x-2 y-2 r2
##                              g1 x-2
##                              g0 zu
##                              g0 x4 y0 '''.split('\n'),
##                       'E':'''g0 zd
##                              g1 y6
##                              g1 x4
##                              g0 zu
##                              g0 x-2 y-3
##                              g0 zd
##                              g1 x-2
##                              g0 zu
##                              g0 y-3
##                              g0 zd
##                              g1 x4
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'F':'''g0 zd
##                              g1 y6
##                              g1 x4
##                              g0 zu
##                              g0 x-2 y-3
##                              g0 zd
##                              g1 x-2
##                              g0 zu
##                              g0 x4 y-3 '''.split('\n'),
##                       'G':'''g0 x2 y3
##                              g0 zd
##                              g1 x2
##                              g1 y-1
##                              g2 x-4 r2
##                              g1 y2
##                              g2 x4 r2
##                              g0 zu
##                              g0 x0 y-4 '''.split('\n'),
##                       'H':'''g0 zd
##                              g1 y6
##                              g0 zu
##                              g0 x4
##                              g0 zd
##                              g1 y-6
##                              g0 zu
##                              g0 x-4 y3
##                              g0 zd
##                              g1 x4
##                              g0 zu
##                              g0 x0 y-3 '''.split('\n'),
##                       'I':'''g0 x1 y6
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x-1
##                              g0 zd
##                              g1 y-6
##                              g0 zu
##                              g0 x-1
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y0 '''.split('\n'),
##                       'J':'''g0 x1 y6
##                              g0 zd
##                              g1 x3
##                              g0 zu
##                              g0 x-1
##                              g0 zd
##                              g1 y-4.5
##                              g2 x-3 r1.5
##                              g1 y0.5
##                              g0 zu
##                              g0 x4 y-2 '''.split('\n'),
##                       'K':'''g0 zd
##                              g1 y6
##                              g0 zu
##                              g0 x4
##                              g0 zd
##                              g1 x-4 y-4
##                              g0 zu
##                              g1 x1 y1
##                              g0 zd
##                              g1 x3 y-3
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'L':'''g0 y6
##                              g0 zd
##                              g1 y-6
##                              g1 x4
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'M':'''g0 zd
##                              g1 y6
##                              g1 x2 y-3
##                              g1 x2 y3
##                              g1 y-6
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'N':'''g0 zd
##                              g1 y6
##                              g1 x4 y-6
##                              g1 y6
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'O':'''g0 y2
##                              g0 zd
##                              g1 y2
##                              g2 x4 r2
##                              g1 y-2
##                              g2 x-4 r2
##                              g0 zu
##                              g0 x4 y-2 '''.split('\n'),
##                       'P':'''g0 zd
##                              g1 y6
##                              g1 x2.5
##                              g2 y-3 r1.5
##                              g1 x-2.5
##                              g0 zu
##                              g0 x4 y-3 '''.split('\n'),
##                       'Q':'''g0 y2
##                              g0 zd
##                              g1 y2
##                              g2 x4 r2
##                              g1 y-2
##                              g2 x-4 r2
##                              g0 zu
##                              g0 x2
##                              g0 zd
##                              g1 x2 y-2
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'R':'''g0 zd
##                              g1 y6
##                              g1 x2.5
##                              g2 y-3 r1.5
##                              g1 x-2.5
##                              g0 zu
##                              g0 x2.5
##                              g0 zd
##                              g1 x1.5 y-3
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'S':'''g0 y2
##                              g0 zd
##                              g3 x4 r2
##                              g3 x-2 y1 r2
##                              g2 x-2 y1 r2
##                              g2 x4 r2
##                              g0 zu
##                              g0 x0 y-4 '''.split('\n'),
##                       'T':'''g0 x2
##                              g0 zd
##                              g1 y6
##                              g0 zu
##                              g0 x-2
##                              g0 zd
##                              g1 x4
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'U':'''g0 y6
##                              g0 zd
##                              g1 y-4
##                              g3 x4 r2
##                              g1 y4
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'V':'''g0 y6
##                              g0 zd
##                              g1 x2 y-6
##                              g1 x2 y6
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'W':'''g0 y6
##                              g0 zd
##                              g1 x1 y-6
##                              g1 x1 y3
##                              g1 x1 y-3
##                              g1 x1 y6
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'X':'''g0 zd
##                              g1 x4 y6
##                              g0 zu
##                              g1 x-4
##                              g0 zd
##                              g1 x4 y-6
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       'Y':'''g0 x2
##                              g0 zd
##                              g1 y3
##                              g1 x-2 y3
##                              g0 zu
##                              g0 x2 y-3
##                              g0 zd
##                              g1 x2 y3
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       'Z':'''g0 y6
##                              g0 zd
##                              g1 x4
##                              g1 x-4 y-6
##                              g1 x4
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       '0':'''g0 y2
##                              g0 zd
##                              g1 y2
##                              g2 x4 r2
##                              g1 y-2
##                              g2 x-4 r2
##                              g0 zu
##                              g0 x1 y1
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y-3 '''.split('\n'),
##                       '1':'''g0 x1 y5
##                              g0 zd
##                              g1 x1 y1
##                              g1 y-6
##                              g0 zu
##                              g1 x-1
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y0 '''.split('\n'),
##                       '2':'''g0 y4
##                              g0 zd
##                              g2 x4 r2
##                              g1 x-4 y-4
##                              g1 x4
##                              g0 zu
##                              g0 x0 y0 '''.split('\n'),
##                       '3':'''g0 y4.5
##                              g0 zd
##                              g2 x2 y1.5 r2
##                              g2 x2 y-1.5 r2
##                              g2 x-2 y-1.5 r2
##                              g2 x2 y-1.5 r2
##                              g2 x-2 y-1.5 r2
##                              g2 x-2 y1.5 r2
##                              g0 zu
##                              g0 x4 y-1.5 '''.split('\n'),
##                       '4':'''g0 x3
##                              g0 zd
##                              g1 y6
##                              g1 x-3 y-4
##                              g1 x4
##                              g0 zu
##                              g0 x0 y-2 '''.split('\n'),
##                       '5':'''g0 y1
##                              g0 zd
##                              g3 x2 y-1 r2
##                              g3 y4 r2
##                              g3 x-2 y-1 r2
##                              g1 y3
##                              g1 x4
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       '6':'''g0 y2
##                              g0 zd
##                              g2 x2 y1 r2
##                              g2 x2 y-1.5 r2
##                              g2 x-2 y-1.5 r2
##                              g2 x-2 y2 r2
##                              g2 x4 y4 r4
##                              g0 zu
##                              g0 x0 y-6 '''.split('\n'),
##                       '7':'''g0 x1
##                              g0 zd
##                              g1 x3 y6
##                              g1 x-4
##                              g0 zu
##                              g0 x1 y-3
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y-3 '''.split('\n'),
##                       '8':'''g0 x2 y3
##                              g0 zd
##                              g2 x-2 y1.5 r2
##                              g2 x2 y1.5 r2
##                              g2 x2 y-1.5 r2
##                              g2 x-2 y-1.5 r2
##                              g2 x2 y-1.5 r2
##                              g2 x-2 y-1.5 r2
##                              g2 x-2 y1.5 r2
##                              g2 x2 y1.5 r2
##                              g0 zu
##                              g0 x2 y-3 '''.split('\n'),
##                       '9':'''g0 zd
##                              g3 x4 y4 r4
##                              g3 x-2 y2 r2
##                              g3 x-2 y-1.5 r2
##                              g3 x2 y-2 r2
##                              g3 x2 y1 r2
##                              g0 zu
##                              g0 x0 y-4 '''.split('\n'),
##                       ' ':'''g0 x4 y0 '''.split('\n'),
##                       '.':'''g0 x2
##                              g0 zd
##                              g2 j0.5
##                              g0 zu
##                              g0 x2 y0 '''.split('\n'),
##                       ',':'''g0 x2
##                              g0 zd
##                              g2 x0.5 y0.5 j0.5
##                              g2 x-1 y-1 i-1
##                              g1 x0.5 y0.5
##                              g0 zu
##                              g0 x2 y0 '''.split('\n'),
##                       '!':'''g0 x2
##                              g0 zd
##                              g2 j0.5
##                              g0 zu
##                              g0 y2
##                              g0 zd
##                              g1 x-0.5 y3.5
##                              g2 x1 r0.5
##                              g1 x-0.5 y-3.5
##                              g0 zu
##                              g0 x2 y-2 '''.split('\n'),
##                       '?':'''g0 x2
##                              g0 zd
##                              g2 j0.5
##                              g0 zu
##                              g0 y2
##                              g0 zd
##                              g1 y1
##                              g3 x2 y1.5 r2
##                              r3 x-2 y1.5 r2
##                              g3 x-2 y-2 r2
##                              g0 zu
##                              g0 x4 y-4 '''.split('\n'),
##                       '-':'''g0 x1 y3
##                              g0 zd
##                              g1 x2
##                              g0 zu
##                              g0 x1 y-3 '''.split('\n'),
##                       }
##              
##              }
##             ]
##        
##w = Writer(1)
##font = w.fonts[0]
##chars = list(font['chars'].items())
##chars.sort()
##chars2 = {}
##for char,coos in chars:
##    coos2 = []
##    for coo in coos:
##        coo2 = [0,0,0,0]
##        for x in coo.split():
##            if x[0] == 'x':
##                num = x[1:]
##                if '.' in num:
##                    num = float(num)
##                else:
##                    num = int(num)
##                coo2[0] = num
##            elif x[0] == 'y':
##                num = x[1:]
##                if '.' in num:
##                    num = float(num)
##                else:
##                    num = int(num)
##                coo2[1] = num
##            elif x[0] == 'z':
##                if x[1] == 'u':
##                    num = 1
##                elif x[1] == 'd':
##                    num = -1
##                else:
##                    print('z error')
##                coo2[2] = num
##            elif x[0] == 'r':
##                num = x[1:]
##                if '.' in num:
##                    num = float(num)
##                else:
##                    num = int(num)
##                coo2[3] = num
##        coos2.append(tuple(coo2))
##    chars2[char] = tuple(coos2)
##print('    fonts = {')
##print('             \'{}\':{{'.format(font['name']))
##print('                       \'chars\':{')
##for char,nada in chars[:]:
##    print('                                \'{}\':({},'.format(char,chars2[char][0]))
##    for c in chars2[char][1:]:
##        print('                                     {},'.format(c))
##    print('                                      ),')
##print('                       },')
##print('             }')












