# notify
print('LOAD: cube.py')

############################
# notes
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
#    SW2 <-- G15 A08 |    | MOSI G18 --> MOSI
#            G32 A07 |    | MISO G19 
#    SW1 <-- G14 A06 |    | RX   G16 --> RX from GPS
#            G22 SCL |    | TX   G17 --> TX to GPS
#            G23 DSA |    |      G21 
#                     ----

############################
# imports
############################

import os,sys,time
from machine import Pin
from random import randint
import urequests

import max7219
import ublox

############################
# class
############################

class CUBE:

    # user vars
    timezone  = -5    # hour offset from GMT
    clocktype = 12    # if 12, use 12 hour clock
    dmode = 1         # default mode on start
    intensity = 0     # start intensity
    useconfig = False # use cube_config.py if avaliable

    # process vars
    idata = {'anypin':{'time':0}} # interrupt data
    bounce = 500 # ms bounce time

    def __init__(self):

        pass

    def read_config(self):
        if self.useconfig and 'cube_config.py' in os.listdir():
            try:
                import cube_config as config
                self.timezone = config.timezone
                self.clocktype = config.clocktype
                self.dmode = config.dmode
                self.intensity = config.intensity
                del config
                print('CONFIG READ')
            except:
                print('CONFIG FILE ERROR')

    def write_config(self):
        with open('cube_config.py',mode='w') as f:
            f.write('timezone = {}\n'.format(self.timezone))
            f.write('clocktype = {}\n'.format(self.clocktype))
            f.write('dmode = {}\n'.format(self.dmode))
            f.write('intensity = {}\n'.format(self.intensity))
            f.close()
            print('CONFIG WRITE')

    def interrupt_callback(self,pin):
        name = str(pin)
        print('INT: {}'.format(name))
        if name in self.idata:
            if time.ticks_diff(time.ticks_ms(),self.idata['anypin']['time']) < self.bounce:
                return
            self.idata[name]['count'] += 1
            self.idata[name]['time'] = time.ticks_ms()
            self.idata['anypin']['time'] = time.ticks_ms()

    def interrupt_clear(self,pin):
        self.idata[str(pin)] = {'count':0,'time':0}

    def interrupt_value(self,pin):
        name = str(pin)
        if name in self.idata:
            print('INT VALUE: {} {}'.format(name,self.idata[name]['count']))
            return self.idata[name]['count']
        return None

    def run(self):

        # major catch (cleans up on error)
        try:

            # config
            self.read_config()
            self.mode = self.dmode

            # set up grid
            grid = max7219.MAX7219_16X16_GRID()
            grid.intensity = self.intensity
            grid.port_open(test=True)

            # set up gps
            gps = ublox.SerialGPS()
            gps.timezone = self.timezone
            gps.port_open()

            # set up button 1
            self.button1 = Pin(14,Pin.IN,Pin.PULL_DOWN)
            self.button1.irq(trigger=Pin.IRQ_RISING,handler=self.interrupt_callback)
            self.interrupt_clear(self.button1)

            # set up button 2
            self.button2 = Pin(15,Pin.IN,Pin.PULL_DOWN)
            self.button2.irq(trigger=Pin.IRQ_RISING,handler=self.interrupt_callback)
            self.interrupt_clear(self.button2)

            # set up buffers
            sbuff = None
            dbuff = None
            zscount = 0 # zero speed count 

            # next time to loop
            nexttime = 0
            looptime = 1.0

            # loop
            while 1:

                # loop time
                while time.time() < nexttime:
                    time.sleep(0.01)
                nexttime = time.time() + looptime

                # update data
                year,month,day,hour,minute,seconds,lat,long,course,knots,kps,mph = gps.get_data()
                print('DATA:',[year,month,day,hour,minute,seconds,lat,long,course,knots,kps,mph])

                # date
                if year == None:
                    year = ''
                    date = ''
                else:
                    year = '{}'.format(year)
                    date = '{}-{}'.format(day,month)

                # time
                if hour == None:
                    hmtime = '-'
                    seconds = '-'
                else:
                    # use gps.timezone to adjust hour offset
                    if self.clocktype == 12:
                        if hour == 0:
                            hour = 12
                        elif hour > 12:
                            hour -= 12
                    hmtime = '{}:{:0>2}'.format(hour,minute)
                    seconds = '{:0>2}'.format(seconds)

                # speed
                if mph == None:
                    if sbuff != None:
                        speed = str(int(round(sbuff,0)))
                    else:
                        speed = ''
                    sbuff = None
                    zscount += 1
                else:
                    if sbuff != None:
                        speed = str(int(round((mph+sbuff)/2,0)))
                    else:
                        speed = str(int(round(mph,0)))
                    sbuff = mph
                    if speed == '0':
                        zscount += 1
                    else:
                        zscount = 0

                # direction
                # save as deviation from 0
                if course == None:
                    if dbuff != None:
                        direction = str(int(round(dbuff,0)))
                    else:
                        direction = ''
                    dbuff = None
                    cardinal = ''
                else:
                    if dbuff != None:
                        direction = int(round((course+dbuff)/2,0))
                        if abs(direction-course) > 90:
                            direction = (direction + 180) % 360
                        direction = str(direction)
                    else:
                        direction = str(int(round(course,0)))
                    dbuff = course
                    cardinal = ['N','NE','E','SE','S','SW','W','NW','N'][int(round(course/45,0))]

                # check intensity select
                if self.interrupt_value(self.button2):
                    self.intensity += 1
                    if self.intensity >= 5:
                        self.intensity = 0
                    self.interrupt_clear(self.button2)
                    self.interrupt_clear(self.button1)
                    grid.set_intensity([0,2,5,9,15][self.intensity])

                # check mode select
                if self.interrupt_value(self.button1):
                    self.mode += 1
                    if self.mode >= 6:
                        self.mode = 1
                    self.interrupt_clear(self.button1)
                    self.interrupt_clear(self.button2)

                # clear frame
                grid.frame_clear()

                # display mode
                grid.bitset(self.mode,16)

                # mode 1 display (time, seconds)
                if self.mode == 1:
                    grid.place_text(hmtime,9,4,font=5,center=True,middle=True,value=1)
                    grid.place_text(seconds,9,12,font=7,center=True,middle=True,value=1)

                # speed modes 2-4
                elif self.mode in (2,3,4):

                    # check for movement
                    if zscount < 2:

                        # mode 2 display (speed, cardinals)
                        if self.mode == 2:
                            grid.place_text(speed,9,5,font=7,center=True,middle=True,value=1)
                            grid.place_text(cardinal,9,13,font=5,center=True,middle=True,value=1)

                        # mode 3 display (speed, azimuth)
                        elif self.mode == 3:
                            grid.place_text(speed,9,5,font=7,center=True,middle=True,value=1)
                            grid.place_text(direction,9,13,font=5,center=True,middle=True,value=1)
                             # mark

                        # mode 4 display (BIG speed)
                        elif self.mode == 4:
                            grid.place_text(speed,9,8,font=11,center=True,middle=True,value=1)

                    # not moving mode (show time)
                    else:
                        grid.place_text(hmtime,9,9,font=5,center=True,middle=True,value=1)

                # mode 5 display (time only)
                elif self.mode == 5:
                    grid.place_text(hmtime,9,9,font=5,center=True,middle=True,value=1)

##                # mode 5 (random)
##                elif self.mode == 5:
##                    for x in range(32):
##                        grid.bitset(randint(1,16),randint(1,16))                        

                # show frame
                grid.frame_show()
            
        # notify
        except Exception as e:
            sys.print_exception(e)

        # clean up
        finally:
            try:
                grid.port_close()
            except:
                pass
            try:
                gps.port_close()
            except:
                pass
            try:
                switch.close()
            except:
                pass

        # save config
        self.write_config()

