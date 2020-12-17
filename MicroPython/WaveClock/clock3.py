# clock3.py
# Copyright (c) 2017 Clayton Darwin
# claytondarwin.com claytondarwin@gmail.com

# notify
print('LOAD: clock3.py')

#---------------------------------------------------------------
# IMPORTANT
#---------------------------------------------------------------

# there is no guarantee I won't disable the time service used below

# need to add a WDT function, clock gets stuck infrequently, should reset

#---------------------------------------------------------------
# variables
#---------------------------------------------------------------

# network
essid = 'your_network'
password = 'your_password'

# time
# NEW: use linux TZ zone in request (see below)
# OLD: timezone = -5
# OLD: daylight_savings = True

# pixel grid
pin = 4
width = 27
height = 9
colors = 3
timing = True
mode = 1
xoffset = -1
yoffset = -1

# colors
mcvalue      = 8
mcscale      = mcvalue/255
notify_red   = tuple([int(round(x*mcscale,0)) for x in (255,0,0)])
notify_green = tuple([int(round(x*mcscale,0)) for x in (0,255,0)])
clock_bg     = tuple([int(round(x*mcscale,0)) for x in (0,0,0)])
clock_fg     = tuple([int(round(x*mcscale,0)) for x in (0,0,255)])
wave_water   = tuple([int(round(x*mcscale,0)) for x in (0,0,128)])
wave_foam    = tuple([int(round(x*mcscale,0)) for x in (128,128,255)])
wave_sand    = clock_bg

# wave
wave_pause = 4.44 # between wave starts
wave_surprise = 444
wave_rfactor = 1.6 # radius multiplier time grid width
wave_steps = 15 # steps (moves) up, then down
wave_min_height = 3
wave_step_pause_base = 0.001 # smaller is faster
wave_x_start_min = -10
wave_x_start_max = 7
    
#---------------------------------------------------------------
# imports
#---------------------------------------------------------------

# imports
import time, npxy
from machine import RTC
from math import sqrt

# this kills all network connections on import
from nettools import wlan_connect, wlan_disconnect
from wget import wget

# random
print('RANDOM 1:',npxy.randint())

#---------------------------------------------------------------
# functions
#---------------------------------------------------------------

class CLOCK:

    def __init__(self):

        # make grid
        self.npg = npxy.NPXY(pin,width,height,colors,timing,mode,xoffset,yoffset)
        self.npg.random_flash(255,100,fast=True)
        self.notify('reset',notify_red)

        # must have times to start
        self.rtc = RTC()
        self.time_ok = False
        while not self.time_ok:
            self.get_times(notify=True)

        # start clock loop
        self.clock_loop()

    def notify(self,text,color=(1,0,0)):
        print('NOTIFY:',text)
        text = text.split()
        for word in text:
            self.npg.clear()
            self.npg.center_text(word,color)
            self.npg.write()
            time.sleep(0.8)
        self.npg.off()

    def get_times(self,notify=False):

        # reset status
        self.time_ok = False

        # notify
        if notify:
            self.notify('get time',notify_green)

        # connect to network
        connected = wlan_connect(essid,password,timeout=30)

        # no connect
        if not connected:
            wlan_disconnect(timeout=15)
            if notify:
                self.notify('no inet',notify_red)
            return False

        # get times
        print('Read Times...',end=' ')
        for x in range(10):
            try:
                # IMPORTANT: there is no guarantee I won't kill this service
                headers,response = wget('http://symple.design/cgi-bin/ztime.py?TZ=New_York',None,True,True,1024)
                response = response.strip().split(b'\n')[-1]
                year,month,day,hour,minute,second = [int(x) for x in response.split()[:6]]
                self.rtc.datetime((year,month,day,None,hour,minute,second,0))
                self.time_ok = True
                print('okay',end=' ')
                break
                # old method used npttime module
                #self.ntptime = ntptime.time()
                #self.cputime = time.time()
                #self.time_ok = True
                #print('okay',end=' ')
                #break
            except:
                self.time_ok = False
                print('wait',end=' ')
                time.sleep(3)
        print('done.')

        # disconnect
        wlan_disconnect(timeout=10)

        # notify
        if notify:
            if self.time_ok:
                self.notify('time okay',notify_green)
            else:
                self.notify('time error',notify_red)
            
    def clock_loop(self):

        # time format machine.RTC().datetime = (year,month,day,weekday,hour,min,second,subsecond)

        lasttime = (0,0) 
        lastwave = 0
        lastcheck = 0
        timegrid = self.tgrid('')
        full = True
        wavecount = 0

        while 1:

            # current time
            year,month,day,weekday,hour,minute,second,subsec = self.rtc.datetime()
            nowsecs = time.ticks_ms()/1000

            # update network time
            if time.time() - lastcheck >= 3600:
                self.get_times(notify=False)
                lastcheck = time.time()
                nowsecs = time.ticks_ms()/1000

            # time changed
            if (hour,minute) != lasttime:
                print('CHANGE:',lasttime,'==>',(hour,minute))

                # get time grid
                ghour = hour
                if ghour > 24:
                    ghour -= 24
                elif ghour > 12:
                    ghour -= 12
                elif ghour <= 0:
                    ghour += 12
                tstring = '{}:{:0>2}'.format(ghour,minute)
                timegrid = self.tgrid(tstring)

                # change with full wave
                full = True

                # update time
                lasttime = (hour,minute)

            # need to do a wave
            if nowsecs >= lastwave + wave_pause:
                if wavecount == wave_surprise:
                    surprise = (8,0,0) # npxy.randRGB(mcvalue)
                    self.wave(timegrid,clock_fg,surprise,wave_foam,wave_sand,wave_steps-5)
                    wavecount = 0
                else:
                    self.wave(timegrid,clock_fg,wave_water,wave_foam,wave_sand,full)
                lastwave = nowsecs
                full = False
                wavecount += 1

            # no change
            else:
                pass

            # add error mark to lower left corner
            if not self.time_ok:
                self.npg.setp(self.npg.width,1,*notify_red)
                self.npg.write()

            # delay
            time.sleep(0.1)

    def wave(self,tgrid,tcolor,water,foam,sand,full=False):

        # setup
        r = self.npg.width*wave_rfactor
        ysteps = wave_steps
        if full:
            if type(full) == int:
                cy = -r - npxy.randint(ysteps-full)
            else:
                cy = -r
            cx = wave_x_start_max/2
        else:
            cy = -r - npxy.randint(ysteps-wave_min_height)
            cx = wave_x_start_min + npxy.randint(wave_x_start_max-wave_x_start_min)
        cx2 = self.npg.width - cx
        xchange = (cx2-cx)/(ysteps+1+ysteps)
        ychange = 1
        pbase = wave_step_pause_base
        wait_until = 0       

        # move circle up cys steps
        for step in range(ysteps):
            while time.ticks_ms()/1000 < wait_until:
                time.sleep(0.001)
            wait_until = (time.ticks_ms()/1000) + (pbase*step**2) 
            cy += ychange
            cx += xchange
            for x in range(self.npg.width):
                y = int(round(sqrt(abs(r**2-(x-cx)**2))+cy,0))
                if y >= 0:
                    if y <= self.npg.height-1:
                        self.npg.setpzf(x,y,foam)
                    for y2 in (y-1,y-2):
                        if 0 <= y2 <= self.npg.height-1:
                            self.npg.setpzf(x,y2,water)
            self.npg.write()

        # peak
        while time.ticks_ms()/1000 < wait_until:
            time.sleep(0.001)
        wait_until = (time.ticks_ms()/1000) + (pbase*step**2) 
        cx += xchange
        for x in range(self.npg.width):
            y = int(round(sqrt(abs(r**2-(x-cx)**2))+cy,0))
            if y >= 0:
                if y <= self.npg.height-1:
                    self.npg.setpzf(x,y,foam)
                for y2 in (y+1,y+2):
                    if 0 <= y2 <= self.npg.height-1:
                        if tgrid[y2][x] == 'X':
                            self.npg.setpzf(x,y2,tcolor)
                        else:
                            self.npg.setpzf(x,y2,sand)
        self.npg.write()
            
        # move circle down cys steps
        for step in range(ysteps-1,-2,-1):
            while time.ticks_ms()/1000 < wait_until:
                time.sleep(0.001)
            wait_until = (time.ticks_ms()/1000) + (pbase*step**2) 
            cy -= ychange
            cx += xchange
            for x in range(self.npg.width):
                y = int(round(sqrt(abs(r**2-(x-cx)**2))+cy,0))
                if 0 <= y <= self.npg.height-1:
                    self.npg.setpzf(x,y,foam)
                # corner error 
                if x <= 3:
                    if 0 <= y+3 <= self.npg.height-1:
                        if tgrid[y+3][x] == 'X':
                            self.npg.setpzf(x,y+3,tcolor)
                        else:
                            self.npg.setpzf(x,y+3,sand)
                # normal
                for y2 in (y+1,y+2):
                    if 0 <= y2 <= self.npg.height-1:
                        if tgrid[y2][x] == 'X':
                            self.npg.setpzf(x,y2,tcolor)
                        else:
                            self.npg.setpzf(x,y2,sand)
            self.npg.write()

    def tgrid(self,text):

        # text
        text = self.npg.fix_text(text,smash=True,strip=True,upper=True)

        # yshift
        char_height = self.npg.chars['height']
        if char_height >= self.npg.height:
            yshift = 0
        else:
            yshift = int( (self.npg.height - char_height) // 2 )

        # xshift
        tlen = sum([self.npg.chars[c][1] for c in text]) + len(text) - 1
        xshift = int( (self.npg.width - tlen) // 2 )

        # grid
        tgrid = [' '*xshift for x in range(char_height)]
        for c in text:
            c2,cwidth,cindex = self.npg.chars[c]
            for y in range(char_height-1,-1,-1):
                tgrid[y] += self.npg.font[y][cindex:cindex+cwidth] + ' '
        xshift = ' '*(self.npg.width - len(tgrid[-1]))
        tgrid = [x+xshift for x in tgrid]                             
        tgrid.insert(0,' '*self.npg.width)
        tgrid.append(tgrid[0])

        # done
        return tgrid

