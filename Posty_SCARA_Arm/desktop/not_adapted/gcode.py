# The Python Pins Project - www.PyPins.com
# Copyright (c) 2016 Clayton Darwin
# Module:   gcode.py
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

#-----------------------------------------------
# Notes
#-----------------------------------------------

# This class is incomplete. The idea is that this is enough to run the output
# from most CAM software, which is generally very limited. In most cases, G1 X- Y- Z- is the
# main code used. This isn't intended to read/send full RS274/NGC GCODE programs.

# This class creates the gcode object (i.e. the GCO).
# The GCO handles reading files and parsing g-code lines.
# The parsed data is then passed to the appropriate function in the stepper motor object (i.e. the SMO).

# NOTE: This class will not work without a fully set up SMO.
# The GCO must be given an SMO on __init__, as in "GMO = GCode(NCO)".
# The SMO must have a NibbleCom Object defined (i.e. NCO, see nibblecom.py).

# NOT ALLOWED: axes(abcuvw), planes G18 G19, variables, parameters, expressions, operators, functions

# ALLOWED BUT NON-FUNCTIONAL: S T 

# PARTIALLY FUNCTIONAL: M6

# FUNCTIONAL: G0 G1 G2 G3 G4 G17 G18 G19 G20 G21 G73 G80 G81 G82 G83 G90 G91 G90.1 G91.1 G98 G99
#             M0 M1 M2 M30 M3 M4 M5 M7 M8 M9
#             X Y Z  I J K  R Q P L  @ ^  F

#-----------------------------------------------
# Imports
#-----------------------------------------------

import os,sys,time,re

#-----------------------------------------------
# Class: G-Code Reader
#-----------------------------------------------

class GCode:

    # ------------------------------------------
    # Init
    # ------------------------------------------

    def __init__(self,smo):

        # set stepper motor object
        self.smo = smo

        # define/clear motor data
        self.clear()

        # holder for axis and switch data
        self.axes = {}
        self.switches = {}

        # swap values (replaced in a line before evaluating)
        self.swaps = []

        # codes allowed
        self.gcodes = 'g0 g1 - g2 g3 - g4 - g17 g18 g19 - g20 g21 - g73 g80 g81 g82 g83 - g90 g90.1 g91 g91.1 - g98 g99 -    '.replace('-',' ').split()
        self.mcodes = 'm0 m1 - m2 m30 - m3 m4 m5 - m6 - m7 m8 m9'.replace('-',' ').split()
        self.xcodes = 'f s - t - i j k - l p q r - x y z - @ ^'.replace('-',' ').split()

        # regular expressions (line is lowered)
        self.wordre = re.compile(r'([a-z@^])\s*([-+]?)\s*0*(\d+(?:\.\d+)?)') # (letter)(sign)(number) allows unknown words
        self.commentre = re.compile(r'\((.*?)(?<!\\)\)') # use group(1) for content

        # chip break travel im mm
        self.chip = 0.5

    # ------------------------------------------
    # Setup
    # ------------------------------------------

    # clear all data
    def clear(self,axis=None):

        # data table
        self.data = {

                     # units
                     'units':'mm',

                     # distance modes
                     'rabs':True, # rays absolute
                     'aabs':True, # arcs absolute

                     # feed rates
                     # based on pauses between steps
                     'xpause':None,
                     'ypause':None,
                     'zpause':None,

                     # speed
                     'speed':None,

                     # plane
                     'plane':'g17',

                     # last movement code
                     'lmc':None, # g0 or g1 only

                     # retract mode (drilling/boring)
                     'retract':'g99', # retract to initial Z

                     # canned cycle data (r,q,p,l)
                     'can':{},

                     # last line parse errors/messages
                     'errors':[],

                     }

    # add an axis
    def addaxis(self,axisname,motorname,units,perstep,minpause):

        axisname = axisname.lower()
        if axisname in ('x','y','z') and motorname in self.smo.motors:

            # all perstep values are converted to mm
            units = units.lower()
            if units.startswith('in'):
                perstep = perstep*25.4

            self.axes[axisname] = (motorname,perstep,minpause)
            return True

        return False

    # add a switch 
    def addswitch(self,switchname,pointaddress,pinnumber,inverse=False):

        # coolant: m7=mist, m8=flood
        # spindle: m3=cw, m4=ccw
        # off commands m5 and m9 use the other switches (don't add a switch for them)

        switchname = switchname.lower()
        if inverse:
            inverse = True
        else:
            inverse = False

        if switchname in ('m3','m4','m7','m8') and \
           type(pointaddress) == int and 1 <= pointaddress <= 15 and \
           type(pinnumber) == int and 0 <= pinnumber <= 3:
            self.switches[switchname] = (pointaddress,pinnumber,inverse)
            return True

        return False

    # add a code swap string
    def addswap(self,value1,value2):

        swap1 = str(value1).strip().lower()
        swap2 = str(value2).strip().lower()

        old = dict(self.swaps)
        old[swap1] = swap2      
        
        self.swaps = list(old.items())

        return True

    # ------------------------------------------
    # File Parser
    # ------------------------------------------

    # read a file, parse lines
    def parsefile(self,filepath,check=False):

        print('FILE:',filepath)

        # check
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        # check run 1 (encoding and % marker check)
        encoding = None
        percent = False
        for option in ('utf-8','latin-1'):
            try:
                infile = open(filepath,mode='r',encoding=option,newline=None)
                for line in infile:
                    line = line.strip()
                    if line and line[0] == '%':
                        percent = True
                infile.close()
                encoding = option
                break
            except UnicodeDecodeError:
                pass
        print('CHECK1: encoding={}, %={}'.format(encoding,percent))

        # check run 2 (word check)
        eod = False
        lc = 0
        infile = open(filepath,mode='r',encoding=encoding,newline=None)
        if percent: # read until first percent
            for line in infile:
                lc += 1
                line = line.strip()
                if line and line[0] == '%':
                    print('CHECK START: line {}'.format(lc))
                    break
        else:
            print('CHECK START: line {}'.format(lc))
        ec = 0
        for line in infile: # check lines
            lc += 1
            success,per,eod,message = self.parseline(line,check=True)
            if not success:
                ec += 1
                print('ERROR: line {} ({})'.format(lc,message))
            elif per or eod:
                eod = True
                print('CHECK END: line {}'.format(lc))
                break
            else:
                #print(message)
                pass
        infile.close()

        # evaluation check outcome
        print('CHECK2: {} lines'.format(lc))
        if not eod:
            print('ERROR: no end of file line')
        if ec:
            print('ERROR: {} line errors detected'.format(ec))
        if ec or not eod:
            a = input('\nErrors detected! Proceed? y/n >').lower().strip()
            if a and a[0] in 'nq':
                return False # i.e. quit

        # process (third read)
        lc = 0
        infile = open(filepath,mode='r',encoding=encoding,newline=None)
        if percent: # read until first percent
            for line in infile:
                lc += 1
                line = line.strip()
                if line and line[0] == '%':
                    print('RUN START: line {}'.format(lc))
                    break
        else:
            print('RUN START: line {}'.format(lc))
        ec = 0
        for line in infile: # check lines
            lc += 1
            success,per,eod,message = self.parseline(line,check=False)
            if not success:
                ec += 1
                print('RUN ERROR: line {} ({})'.format(lc,message))
            if per or eod:
                print('RUN END: line {}'.format(lc))
                break
        infile.close()
        if ec:
            print('RUN ERROR: {} line errors detected'.format(ec))
        print('RUN COMPLETE.')

        # done
        return True

    # ------------------------------------------
    # Line Parser
    # ------------------------------------------

    def parseline(self,line,check=False):

        # return  bool_success,bool_percent,bool_end_of_data,message

        # -----
        # parse

        # variables
        linenum = ''
        comments = []
        words = []
        self.data['errors'] = [] # clear line process values
        eof = False # end of file via M2 M30

        # prep
        line = line.strip().lower()

        # swap (post lower)
        for a,b in self.swaps:
            line = line.replace(a,b)

        # check
        if not line:
            return True,False,False,'blank line'

        # block/line delete
        if line.startswith('/'):
            return True,False,False,'block delete "/"'

        # percent code (start/end file)
        elif line.startswith('%'):
            return True,True,False,'percent line "%"'

        # comments
        comments = [' '.join(x.split()) for x in self.commentre.findall(line)]
        line = self.commentre.sub(' ',line)
        if ';' in line:
            i = line.index(';')
            comments.append(' '.join(line[i+1:].split()))
            line = line[:i]

        # words
        for letter,sign,number in self.wordre.findall(line):
            number = eval(sign+number)

            # line number
            if letter == 'n':
                linenum = 'n{}'.format(number)

            # end of file (check only, otherwise go through execute)
            elif check and letter == 'm' and number in (2,30):
                return True,False,True,'end of data "m{}"'.format(number)
            
            elif (letter == 'g' and 'g{}'.format(number) in self.gcodes) or \
                 (letter == 'm' and 'm{}'.format(number) in self.mcodes) or \
                 (letter in self.xcodes):
                words.append((letter,number))

            # report unknown word
            elif check:
                return False,False,False,'unknown word "{}{}"'.format(letter,number)

            # else ignore (if not check)
            else:
                pass

        # nothing to do
        if (not words) and (not comments):
            return False,False,False,'unknown line error'

        # send back formatted line
        elif check:
            words = ['{}{}'.format(*x) for x in words]
            if linenum:
                words.insert(0,linenum)
            if comments:
                words.append(';')
                words += comments
            return True,False,False,' '.join(words).upper()

        # -----
        # execute

        # split words into types
        codes = set()
        values = {}
        for item,value in words:
            if item in 'gm':
                codes.add('{}{}'.format(item,value))
            else:
                values[item] = value

        # get values
        x = values.get('x',None) # x axis movement
        y = values.get('y',None) # y axis movement
        z = values.get('z',None) # z axis movement
        i = values.get('i',None) # x axis center
        j = values.get('j',None) # y axis center
        k = values.get('k',None) # z axis center
        l = values.get('l',None) # cycle permutations
        p = values.get('p',None) # arc rotations
        q = values.get('q',None) # drill cycle delta
        r = values.get('r',None) # arc radius, drill retract
        polara = values.get('^',None) # polar angle
        polard = values.get('@',None) # polar distance
        f = values.get('f',None) # feed speed per minute
        s = values.get('s',None) # spindle speed (undefined)
        t = values.get('t',None) # tool select

        # all distances are mm internally
        if self.data['units'] != 'mm':
            x = self.fixunits(x)
            y = self.fixunits(y)
            z = self.fixunits(z)
            i = self.fixunits(i)
            j = self.fixunits(j)
            k = self.fixunits(k)
            q = self.fixunits(q)
            r = self.fixunits(r)
            polard = self.fixunits(polard)
            f = self.fixunits(f)
        
        # Order based on http://linuxcnc.org/docs/html/gcode/overview.html#_g_code_order_of_execution
        # 1) (not handled) O-word commands (optionally followed by a comment but no other words allowed on the same line)

        # 2) comments/messages
        if comments:
            self.comments(comments)

        # 3) (not handled) Set feed rate mode (G93, G94).

        # 4) Set feed rate (F).
        if f:
            self.feed(f)

        # 5) Set spindle speed (S).
        if s:
            self.speed(s)

        # 6) Select tool (T).
        if t:
            self.tool(t)

        # 7) (not handled) HAL pin I/O (M62-M68).

        # 8) (not handled) Change tool (M6) and Set Tool Number (M61).
        if 'm6' in codes:
            self.toolchange()

        # 9) Spindle on or off (M3, M4, M5).
        if   'm5' in codes:
            self.switch('m5',0,'SWITCH: Spindle OFF:')
        elif 'm4' in codes:
            self.switch('m4',1,'SWITCH: Spindle ON CCW:')
        elif 'm3' in codes:
            self.switch('m3',1,'SWITCH: Spindle ON CW:')

        # 10) (not handled) Save State (M70, M73), Restore State (M72), Invalidate State (M71).

        # 11) Coolant on or off (M7, M8, M9).
        if   'm9' in codes:
            self.switch('m9',0,'SWITCH: Coolant OFF:')
        elif 'm8' in codes:
            self.switch('m8',1,'SWITCH: Coolant FLOOD:')
        elif 'm7' in codes:
            self.switch('m7',1,'SWITCH: Coolant MIST:')

        # 12) (not handled) Enable or disable overrides (M48, M49,M50,M51,M52,M53).
        # 13) (not handled) User-defined Commands (M100-M199).

        # 14) Dwell (G4).
        if 'g4' in codes:
            self.pause(seconds=p)

        # 15) Set active plane (G17, G18, G19).
        if   'g17' in codes:
            self.plane('g17')
        elif 'g18' in codes:
            self.plane('g18')
        elif 'g19' in codes:
            self.plane('g19')

        # 16) Set length units (G20, G21).
        if 'g21' in codes:
            self.units('g21')
        elif 'g20' in codes:
            self.units('g20')

        # 17) (not handled) Cutter radius compensation on or off (G40, G41, G42)

        # 18) (not handled) Cutter length compensation on or off (G43, G49)

        # 19) (not handled) Coordinate system selection (G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3).
        # 20) (not handled) Set path control mode (G61, G61.1, G64)

        # 21) Set distance mode (G90, G91).
        if 'g90' in codes:
            self.dmode('g90')
        elif 'g91' in codes:
            self.dmode('g91')
        if 'g90.1' in codes:
            self.dmode('g90.1')
        elif 'g91.1' in codes:
            self.dmode('g91.1')

        # 22) Set retract mode (G98, G99).
        if   'g98' in codes:
            self.retract('g98')
        elif 'g98' in codes:
            self.retract('g98')

        # 23) (not handled) Go to reference location (G28, G30) or change coordinate system data (G10) or set axis offsets (G92, G92.1, G92.2, G94).

        # 24) Perform motion (G0 to G3, G33, G38.x, G73, G76, G80 to G89), as modified (possibly) by G53.

        # 24a) rays
        if   'g0' in codes:
            self.ray(x,y,z,polara,polard,'g0')
        elif 'g1' in codes:
            self.ray(x,y,z,polara,polard,'g1')           

        # 24b) arcs
        elif 'g2' in codes:
            self.arc(x,y,z,i,j,k,r,p,'g2')
        elif 'g3' in codes:
            self.arc(x,y,z,i,j,k,r,p,'g3')

        # 24c) drill g73
        elif 'g73' in codes:
            self.drill(x,y,z,r,q,p,l,'g73')

        # 24d) drill cycle cancel
        elif 'g80' in codes:
            self.xcycle()

        # 24e) drill cycles g81 g82 g83
        elif 'g81' in codes:
            self.drill(x,y,z,r,q,p,l,'g81')
        elif 'g82' in codes:
            self.drill(x,y,z,r,q,p,l,'g82')
        elif 'g83' in codes:
            self.drill(x,y,z,r,q,p,l,'g83')

        # 24f) unspecified g0 or g1
        elif (x,y,z) != (None,None,None) or (polara != None and polard != None):
            if self.data['lmc'] == 'g0':
                self.ray(x,y,z,polara,polard,'g0')
            elif self.data['lmc'] == 'g1':
                self.ray(x,y,z,polara,polard,'g1')
            elif self.data['lmc'] == 'g81':
                self.drill(x,y,z,r,q,l,p,'g81')
            elif self.data['lmc'] == 'g82':
                self.drill(x,y,z,r,q,l,p,'g82')
            elif self.data['lmc'] == 'g83':
                self.drill(x,y,z,r,q,l,p,'g83')
            else:
                print('ERROR: Coordinates given when movement not selected.')
        
        # 25) Stop (M0, M1, M2, M30, M60).

        # 25a) pause
        if 'm0' in codes:
            self.pause(wait=True)
        elif 'm1' in codes:
            self.pause(wait=True)

        # 25b) end of data
        if 'm30' in codes:
            self.eof()
            eof = True
        elif 'm2' in codes:
            self.eof()
            eof = True 

        # return
        if self.data['errors']:
            return False,False,eof,':'.join([' '.join(x.split()) for x in errors])
        else:
            return True,False,eof,'OK'
        

    # ------------------------------------------
    # Functions
    # ------------------------------------------

    # active comments
    def comments(self,comments):

        if not comments:
            self.data['lpv'].append(True)
            return True

        for comment in comments:
            title = None
            
            if comment.lower().startswith('msg'):
                title = 'MSG:'
                comment = comment[3:]
            elif comment.lower().startswith('print'):
                title = 'PRINT:'
                comment = comment[5:]
            elif comment.lower().startswith('debug'):
                title = 'DEGUG:'
                comment = comment[5:]
            elif comment.lower().startswith('coo'):
                title = 'XYZ:'
                comment = str((round(x,4) for x in self.smo.ccoo()))            

            if title:        
                while comment and comment[0] in ' ,:':
                    comment = comment[1:]
                print(title,comment)

        return True

    # feed rate
    def feed(self,rate):

        # rate = maximum distance per minute for all axes
        # all axses have same feed rate (although pauses may be different)

        # check
        if rate <= 0 or type(rate) not in (int,float):
            print('FEED: ERROR:',rate)
            return False

        # set all axes even if not defined in self.axes
        for axis,axispause in (('x','xpause'),
                               ('y','ypause'),
                               ('z','zpause'),
                               ):
            if axis in self.axes:
                motorname,perstep,minpause = self.axes[axis]

                # 60sec     1min     distance   sec
                # ----- * -------- * -------- = ---- = pause
                #  1min   distance     step     step
                
                self.data[axispause] = max(minpause,(60*perstep)/rate)

        print('FEED:',rate)
        return True

    # spindle rate
    def speed(self,rate):

        # check
        if rate <= 0 or type(rate) not in (int,float):
            print('FEED: ERROR:',rate)
            return False

        # set
        self.data['speed'] = abs(rate)
        print('SPEED:',abs(rate))
        return True

    # tool select
    def tool(self,toolnumber):

        print('TOOL:',toolnumber)
        return True

    # tool change
    def toolchange(self):

        # save current axis locations
        xcurrent = self.smo.motors[self.axes['x'][0]]['steps']
        ycurrent = self.smo.motors[self.axes['y'][0]]['steps']
        zcurrent = self.smo.motors[self.axes['z'][0]]['steps']

        print('DEFAULT TOOL CHANGE: This function should be replaced by the user.')
        print('WARNING: This can cause damage. Be careful.')
        print('MOVE ORDER: --> Z --> Y --> X for axes given per move.')
        print('Absolute Move Example: "z99 y-99"')
        print('Relative Move Example: "r z99 y-99" (i.e. put an "r" in front).')
        print('To QUIT and restart program use "q" or "quit" (case insentitive).')
        print()

        while 1:
            a = input('Move:> ').strip().lower()
            if a:
                if a[0] in 'q':
                    break
                else:
                    if a.startswith('r'):
                        relative = True
                        a = a[1:]
                    else:
                        relative = False
                    words = {}
                    for letter,sign,number in self.wordre.findall(a):
                        if letter in 'zyx':
                            number = eval(sign+number)
                            words[letter] = number
                    for letter in 'zyx':
                        if letter in words:
                            if relative:
                                self.smo.move(self.axes[letter][0],number)
                            else:
                                self.smo.moveto(self.axes[letter][0],number)       

        # return to saved locations
        input('RETURN: --> X --> Y --> Z\nPress ENTER to return to original location.')
        self.smo.stepto(self.axes['x'][0],xcurrent)
        self.smo.stepto(self.axes['y'][0],ycurrent)
        self.smo.stepto(self.axes['z'][0],zcurrent)

        return True

    # switch on/off
    def switch(self,switchname,state=0,comment=None):

        name = switchname.lower()

        if state:
            state = 1
        else:
            state = 0

        prnt = True
        rvalue = False
        
        if comment == None:
            prnt = False
        elif not comment:
            print('SWITCH {}: {}:'.format(switchname,('OFF','ON')[state]),end=' ')
        else:
            print(comment,end=' ')

        # spindle: m3=cw, m4=ccw, m5=stop
        # coolant: m7=mist, m8=flood, m9=off

        # m5: spindle off
        if name == 'm5':
            m3 = self.switch('m3',0)
            m4 = self.switch('m4',0)
            if m3 or m4:
                rvalue = True

        # m9: coolant off
        elif name == 'm9':
            m7 = self.switch('m7',0)
            m8 = self.switch('m8',0)
            if m7 or m8:
                rvalue = True

        # any other
        elif name in self.switches:

            # switch data
            address,pin,inverse = self.switches[name]

            # reset state
            if inverse:
                if state:
                    state = 0
                else:
                    state = 1

            # get current state
            self.smo.nco.tx(0,4) # digital read io on next byte
            self.smo.nco.tx(address,1) # which point
            datum = self.smo.nco.rx(-1,form='ints') # [(address,states)] where address should be 0
            current = datum[0][1]

            # set high
            if state:
                # for OR '0001'=1 '0010'=2 '0100'=4 '1000'=8
                select = (1,2,4,8)[pin]
                new = current | select

            # set low
            else:
                # for AND '1110'=14 '1101'=13 '1011'=11 '0111'=7
                select = (14,13,11,7)[pin]
                new = current & select

            # set new
            self.smo.nco.tx(address,new)
            self.smo.nco.xx(count=False)

            rvalue = True

        # error
        else:
            rvalue = False

        # done
        if prnt:
            print(rvalue)
        return rvalue

    # pause
    def pause(self,seconds=None,wait=False):

        if seconds:
            print('DWELL: {} sec.'.format(seconds),end=' ');sys.stdout.flush()
            try:
                time.sleep(seconds)
                print('Done.')
            except KeyboardInterrupt:
                print('Keyboard Interrupt.')
            except:
                print()
                print('DWELL: Error: Seconds format: "{}"'.format(seconds))
                input('PAUSE: Press ENTER to continue.')
                return False

        if wait:
            input('PAUSE: Press ENTER to continue.')

        return True

    # planes
    def plane(self,plane):

        if plane == 'g17':
            self.data['plane'] = 'g17'
            print('PLANE: XY ({})'.format(plane.upper()))

        elif plane == 'g18':
            self.data['plane'] = 'g18'
            print('PLANE: XZ ({})'.format(plane.upper()))

        elif plane == 'g19':
            self.data['plane'] = 'g19'
            print('PLANE: YZ ({})'.format(plane.upper()))

        else:
            print('PLANE ERROR: {}'.format(plane.upper()))
            return False

        return True

    # units change
    def units(self,units):

        units = units.lower()

        if units in ('g20','in'):
            self.data['units'] = 'in'
            return True
        
        elif units in ('g21','mm'):
            self.data['units'] = 'mm'
            return True

        print('UNITS ERROR: {}'.format(units.upper()))
        return False

    # fix units
    def fixunits(self,value):

        # all internal units are in mm
        # so, it the input is in inches (not mm)
        # multiply by 2.54

        if value == None:
            return None

        elif self.data['units'] == 'mm':
            return value

        else:
            return value * 25.4

    # distance mode
    def dmode(self,mode):

        if mode == 'g90':
            self.data['rabs'] = True
            return True

        elif mode == 'g91':
            self.data['rabs'] = False
            return True

        elif mode == 'g90.1':
            self.data['aabs'] = True
            return True

        elif mode == 'g91.1':
            self.data['aabs'] = False
            return True

        print('MODE ERROR: {}'.format(mode.upper()))
        return False       

    # linear move
    def ray(self,x,y,z,polara,polard,code):

        # last movement code
        self.data['lmc'] = code

        # feed rate
        if code == 'g0':
            xpause = None
            ypause = None
            zpause = None
        else:
            xpause = self.data['xpause']
            ypause = self.data['ypause']
            zpause = self.data['zpause']

        # polar coordinates (always relative)
        if polara and polard:
            return self.smo.polarmove(((self.axes['x'][0],None,xpause),(self.axes['y'][0],None,ypause)),polara,polard)

        # ray
        else:

            # compile
            targets = []
            if x != None:
                targets.append((self.axes['x'][0],x,xpause))
            if y != None:
                targets.append((self.axes['y'][0],y,ypause))
            if z != None:
                targets.append((self.axes['z'][0],z,zpause))

            # none
            if not targets:
                return False

            # absolute
            elif self.data['rabs']:

                # one axis
                if len(targets) == 1:
                    name,value,pause = targets[0]
                    return self.smo.moveto(name,value,pause)

                # multi axis
                else:
                    return self.smo.raymoveto(targets)

            # relative
            else:

                # one axis
                if len(targets) == 1:
                    name,value,pause = targets[0]
                    return self.smo.move(name,value,pause)

                # multi axis
                else:
                    return self.smo.raymove(targets)

    # arc move
    def arc(self, x,y,z, i,j,k, r, p, code):

        # last movement code
        self.data['lmc'] = None

        # feed rate
        if code == 'g0':
            xpause = None
            ypause = None
            zpause = None
        else:
            xpause = self.data['xpause']
            ypause = self.data['ypause']
            zpause = self.data['zpause']

        # XY plane
        if self.data['plane'] == 'g17':

            if 'x' not in self.axes or 'y' not in self.axes:
                raise ValueError('Arcs in G17 require X and Y.')

            xdata = [self.axes['x'][0],x,xpause] # [name,value,pause]
            ydata = [self.axes['y'][0],y,ypause]

            if 'z' in self.axes:
                zdata = [self.axes['z'][0],z,zpause]
            else:
                zdata = [None,None,None]

            center = [i,j]

        # XZ plane
        elif self.data['plane'] == 'g18':

            if 'x' not in self.axes or 'z' not in self.axes:
                raise ValueError('Arcs in G18 require X and Z.')

            xdata = [self.axes['x'][0],x,xpause] # [name,value,pause]
            ydata = [self.axes['z'][0],z,zpause]

            if 'y' in self.axes:
                zdata = [self.axes['y'][0],y,ypause]
            else:
                zdata = [None,None,None]

            center = [i,k]

        # YZ plane
        elif self.data['plane'] == 'g19':

            if 'y' not in self.axes or 'z' not in self.axes:
                raise ValueError('Arcs in G19 require Y and Z.')

            xdata = [self.axes['y'][0],y,ypause] # [name,value,pause]
            ydata = [self.axes['z'][0],z,zpause]

            if 'x' in self.axes:
                zdata = [self.axes['x'][0],x,xpause]
            else:
                zdata = [None,None,None]

            center = [j,k]

        # plane error
        else:
            print('PLANE ERROR:',self.data['plane'])
            return False

        # end point missing values (helix axis can be None)
        if xdata[1] == None:
            xdata[1] = self.smo.motors[xdata[0]]['steps']*self.smo.motors[xdata[0]]['perstep']
        if ydata[1] == None:
            ydata[1] = self.smo.motors[ydata[0]]['steps']*self.smo.motors[ydata[0]]['perstep']

        # bother center values missing
        if center == [None,None]:
            if not r:
                return False
        # or one missing
        elif center[0] == None:
            center[0] = xdata[1]
        elif center[1] == None:
            center[1] = ydata[1]

        # compile targets
        targets = [xdata,ydata]
        if zdata[1] != None:
            targets.append(zdata)

        # none
        if not targets:
            return False

        # rotation
        rotation = 1
        if code in ('g2','-1',-1):
            rotation = -1

        # target arc absolute distances
        if self.data['aabs']:
            startpoint,endpoint,center,rangle,radius = self.smo.arcmoveto(targets,center,r,rotation)

        # target arc relative distance (return values are absolute)
        else:
            startpoint,endpoint,rangle,radius = self.smo.arcmove(targets,center,r,rotation)

        # extra turns
        if p and p > 1:

            # adjust helix for 360 degrees (targets psudo X,Y are the current location)
            if len(targets) == 3:
                targets[2][1] = targets[2][1]*(360/rangle)

            # iterate absolute distances
            for x in range(int(p)-1):
                self.smo.arcmoveto(targets,center,radius,rotation,360)

        # done
        return True

    # drill retract mode
    def retract(self,code):

        if code == 'g98':
            self.data['retract'] = 'g98'
            print('RETRACT to R')
            return True

        elif code == 'g99':
            self.data['retract'] = 'g99'
            print('RETRACT to Zi')
            return True

        return False

    # cancel cycles (G80)
    def xcycle(self):

        # last movement code
        self.data['lmc'] = None

        # canned data
        self.data['can'] = {}

        return True

    # drill
    def drill(self,x,y,z,r,q,p,l,code):

        # last movement code
        self.data['lmc'] = code

        # drilling requires three axes
        missing = None
        if 'x' not in self.axes:
            missing = 'X'
        elif 'y' not in self.axes:
            missing = 'Y'
        elif 'z' not in self.axes:
            missing = 'Z'
        if missing:
            self.data['lmc'] = None
            raise ValueError('Drill cycles require {} axis.'.format(missing))

        # XY plane pseudo axis data
        if self.data['plane'] == 'g17':
            xname,xpause = self.axes['x'][0],self.data['xpause']
            yname,ypause = self.axes['y'][0],self.data['ypause']
            zname,zpause = self.axes['z'][0],self.data['zpause']
            x,y,z = x,y,z

        # XZ plane pseudo axis data
        elif self.data['plane'] == 'g18':
            xname,xpause = self.axes['x'][0],self.data['xpause']
            yname,ypause = self.axes['z'][0],self.data['zpause']
            zname,zpause = self.axes['y'][0],self.data['ypause']
            x,y,z = x,z,y

        # YZ plane pseudo axis data
        elif self.data['plane'] == 'g19':
            xname,xpause = self.axes['y'][0],self.data['ypause']
            yname,ypause = self.axes['z'][0],self.data['zpause']
            zname,zpause = self.axes['x'][0],self.data['xpause']
            x,y,z = y,z,x

        # all axes and data is swapped to psuedo values
        # use x,y drill z from now on

        # current absolute locations
        xstart,ystart,zstart = self.smo.ccoo(xname,yname,zname)

        # convert relative locations to absolute
        # add missing values later
        # NOTE: q is always relative (don't modify)
        if not self.data['rabs']:
            if x != None:
                x = xstart + x
            if y != None:
                y = ystart + y
            if z != None:
                z = zstart + z
            if r != None:
                r = zstart + r

        # g73 non-cycle drill
        if code == 'g73':

            # bad data will generally move XY but not drill

            # add missing values
            # g73 does not use canned values
            # default to do-nothing for movement
            if x == None:
                x = xstart
            if y == None:
                y = ystart
            if z == None:
                z = zstart
            if r == None:
                r = zstart
            if q == None:
                q = None
            if not l or l < 1:
                l = 1
            else:
                l = int(l)

            # set XY add values for loops
            xadd = x - xstart
            yadd = y - ystart

            # all cycles require zstart to be at least as high as r
            # move up to r plane
            if zstart < r:
                print('ERROR: Start Z plane lower than R plane.')
                self.smo.moveto(zname,r,None)
                zstart = r

            # do L cycles
            for cycle in range(l):

                # rapid move to x,y offsets
                self.smo.raymoveto(((xname,x,None),(yname,y,None)))

                # update point for next loop
                x += xadd
                y += yadd

                # rapid move to r plane
                self.smo.moveto(zname,r,None)                

                # iterate until z is reached
                depth = r
                while q and depth > z:

                    # set new depth target (but not below z)
                    depth = max(z,depth-q)

                    # move z axis to target depth at speed f
                    self.smo.moveto(zname,depth,zpause)

                    # chip break (rapid up and down)
                    self.smo.move(zname,self.chip,None)
                    self.smo.move(zname,-self.chip,None)

                # retract to zstart
                if self.data['retract'] == 'g98':
                    self.smo.moveto(zname,zstart,None)

                # retract to r plane
                else:
                    self.smo.moveto(zname,r,None)

        # cycle drill
        else:

            # bad data will generally move XY but not drill

            # add missing values
            # use stored cycle data if possible
            # default to do-nothing for movement

            xadd = self.data['can'].get('xadd',0)
            yadd = self.data['can'].get('yadd',0)

            if x == None:
                x = xstart + xadd
            else:
                xadd = x - xstart

            if y == None:
                y = ystart + yadd
            else:
                yadd = y - ystart

            if z == None:
                z = self.data['can'].get('z',zstart)
            if r == None:
                r = self.data['can'].get('r',zstart)
            if q == None:
                q = self.data['can'].get('q',None)
            if p == None:
                p = self.data['can'].get('p',0)
            if not l or l < 1:
                l = self.data['can'].get('l',1)
            else:
                l = int(l)

            # all cycles require zstart to be at least as high as r
            # move up to r plane
            if zstart < r:
                print('ERROR: Start Z plane lower than R plane.')
                self.smo.moveto(zname,r,None)
                zstart = r

            # do L cycles
            for cycle in range(l):

                # rapid move to x,y offsets
                self.smo.raymoveto(((xname,x,None),(yname,y,None)))

                # update point for next loop
                x += xadd
                y += yadd

                # rapid move to r plane
                self.smo.moveto(zname,r,None)

                # g81 shallow drill
                if code == 'g81':

                    # move z axis to z depth at speed f
                    self.smo.moveto(zname,z,zpause)

                # g82 shallow drill with dwell
                elif code == 'g82':

                    # move z axis to z depth at speed f
                    self.smo.moveto(zname,z,zpause)

                    # dwell
                    time.sleep(p)

                # g83 deep drill with peck
                elif code == 'g83':

                    # iterate until z is reached
                    depth = r
                    while q and depth > z:

                        # set new depth target (but not below z)
                        depth = max(z,depth-q)

                        # move z axis to target depth at speed f
                        self.smo.moveto(zname,depth,zpause)

                        # rapid retract to r plane
                        self.smo.moveto(zname,r,None)

                        # rapid return to depth
                        if depth > z:
                            self.smo.moveto(zname,depth,None)

                # retract to zstart
                if self.data['retract'] == 'g98':
                    self.smo.moveto(zname,self.data['can'].get('zstart',zstart),None)

                # retract to r plane
                else:
                    self.smo.moveto(zname,r,None)

            # store/can cycle values
            # NOTE: only store non-None values
            self.data['can'] = dict([(x,y) for x,y in [('xadd',xadd),
                                                       ('yadd',yadd),
                                                       ('zstart',zstart),
                                                       ('z',z),
                                                       ('r',r),
                                                       ('q',q),
                                                       ('p',p),
                                                       ('l',l)] if y != None])

        return True

    # end of file
    def eof(self):

        self.switch('m5',0)
        self.switch('m9',0)
        self.clear()
        return True


