#-----------------------------------------------
# netmon2.py
#-----------------------------------------------

# notify
print('RUN: netmon2.py (Network Monitor)')

#-----------------------------------------------
# imports
#-----------------------------------------------

# import standard library
import os,sys,time,gc,json
from machine import RTC, WDT
import urequests

# import local network
from nettools import *
import netcreds as my

# import other local libraries 
import eziot_micropython_minimal as eziot
import max7219_32x16
import beeper

# wdt catch
print('PAUSE before WDT')
for x in range(10):
    time.sleep_ms(100)

# clean up
gc.collect()

#-----------------------------------------------
# setup
#-----------------------------------------------

# beeper pin
beeppin = 27

# grid pins/values
grid_mosi = 13
grid_sck  = 14
grid_cs   = 15
grid_intensity = 0

# network check loop
loop_every = 10 # if minutes % loop_every == 0

# server checks
servers = [
    ('BRDI','http://192.168.254.100'),
    ('ILLNC','http://illocutioninc.com'),
    ('BRDCB','http://broadriverdata.com/cgi-bin/stime.py'),
    ]

# stock checks
stocks = ['DOCN']

#-----------------------------------------------
# class
#-----------------------------------------------

class NETMON:

    def __init__(self):

        # watchdog
        # note that urequests has a 30 sec timeout
        self.wdt = WDT(timeout=60000)

        # real time clock
        self.rtc = RTC()

        # make grid
        self.grid = max7219_32x16.MAX7219_32X16_GRID()
        self.grid.mosi = grid_mosi
        self.grid.sck  = grid_sck
        self.grid.cs   = grid_cs
        self.grid.intensity = grid_intensity
        self.grid.port_open(test=False)

        # display variables
        self.youtube = [0,0] # [subs,views]
        self.stock_values = {} # {name:(value,change)} pairs
        self.weather = [0,0,0] # [temp,press,humidity]
        
    def run(self):

        # run forever
        while 1:
            self.wdt.feed()

            # full catch
            try:

                # start main beep
                beeper.beep3(beeppin,2200,4400,0.25)
                time.sleep_ms(100)
##                beeper.beep3(beeppin,2200,4400,0.133)
##                time.sleep_ms(100)
##                beeper.beep3(beeppin,2200,4400,0.133)
##                time.sleep_ms(100)
##                beeper.beep3(beeppin,2200,4400,0.133)
##                time.sleep_ms(100)
##                beeper.beep3(beeppin,2200,4400,0.125)
##                beeper.beep3(beeppin,4400,2200,0.6);

                # variables
                xservers = []
                minute = 0
                last_check = -1 # start condition

                # connect to wifi
                wlan_connect(my.essid,my.essid_password)

                # loop inside
                loops = 0
                while 1:
                    self.wdt.feed()

                    # wait for next loop time
                    print('LOOP:',loops)

                    #-----------------------------------------------
                    # display until check loop time
                    #-----------------------------------------------

                    #while time.ticks_diff(self.next_loop,time.ticks_ms()) > 0:
                    while last_check >= 0 and (last_check == minute or minute%loop_every != 0):
                        self.wdt.feed()

                        # display time
                        year,month,day,junk,hour,minute,second,junk = self.rtc.datetime()
                        self.grid.canvas()
                        self.grid.place_text('{}:{:0>2}'.format(hour,minute),16,4,7)
                        self.grid.frame_show()

                        # build scrolling text
                        text = ' '*8
                        # date
                        month = {1:'JAN',2:'FEB',3:'MAR',4:'APR',5:'MAY',6:'JUN',7:'JUL',8:'AUG',9:'SEP',10:'OCT',11:'NOV',12:'DEC',}.get(month,None)
                        text += '{} {}'.format(month,day)
                        # youtube
                        text += '    subs {:.1f} K    views {:.2f} M'.format(*self.youtube)
                        # stocks
                        for name,(value,change) in self.stock_values.items():
                            symbol = ''
                            if change > 0:
                                symbol = '+'
                            text += '    {} {:.2f} {}{:.2f} %'.format(name,value,symbol,change)
                        # weather
                        text += '    temp {:.1f} F    bp {:.1f} in    rh {:.1f} %'.format(*self.weather)
                        text += ' '*8
                        self.grid.scroll_text(text,13,7,middle=True,pause=40,preclear=False,postclear=False,leaveit=True,canvasit=False)

                    #-----------------------------------------------
                    # check sequence
                    #-----------------------------------------------
                    
                    # set up next loop
                    loops += 1

                    # clean
                    gc.collect()

                    # set data
                    xservers = []

                    # check and set time
                    try:
                        self.wdt.feed()
                        print('Checking ZTime...')
                        self.grid.cclear()
                        self.grid.place_text('time',16,4,7)
                        self.grid.place_text('check',16,13,7)
                        self.grid.frame_show()
                        # IMPORTANT: there is no guarantee I won't kill this service
                        r = urequests.get('http://claytondarwin.com/cgi-bin/ztime.py?TZ=New_York')
                        data = r.content.strip()
                        r.close()
                        print('DATA:',[data])
                        if not data:
                            raise ValueError('ZTime returned no usable data.')
                        data = data.split(b'\n')[-1]
                        year,month,day,hour,minute,second = [int(x) for x in data.split()[:6]]
                        self.rtc.datetime((year,month,day,None,hour,minute,second,0))
                        last_check = minute
                        print('TIME OKAY: {:0>4}-{:0>2}-{:0>2} {:0>2}:{:0>2}:{:0>2}'.format(year,month,day,hour,minute,second))
                        self.grid.canvas()
                        self.grid.place_text('time',16,4,7)
                        self.grid.place_text('OKAY',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(500)
                        self.grid.cclear()
                    except Exception as e:
                        beeper.beep(beeppin,220,0.5)
                        print('\n-----\n')
                        print('ZTime error.')
                        sys.print_exception(e)
                        xservers.append('ZTIME')
                        self.grid.canvas()
                        self.grid.place_text('time',16,4,7)
                        self.grid.place_text('ERROR',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(1000)
                        self.grid.cclear()

                    # check and set youtube
                    try:
                        self.wdt.feed()
                        print('Checking YouTube API...')
                        self.grid.canvas()
                        self.grid.place_text('ytube',16,4,7)
                        self.grid.place_text('check',16,13,7)
                        self.grid.frame_show()
                        r = urequests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&key={}&forUsername=drsimpleton'.format(my.youtube_api_key))
                        data = r.content.strip()
                        r.close()                
                        if not data:
                            raise ValueError('YouTube returned no usable data.')
                        data = json.loads(data)
                        if data:
                            if 'items' in data:
                                items = data['items']
                                if items:
                                    if 'statistics' in items[0]:
                                        stats = items[0]['statistics']
                                        # subscribers
                                        if 'subscriberCount' in stats:
                                            subs = int(stats['subscriberCount'])
                                            subs /= 1000
                                            self.youtube[0] = subs
                                            print('SUBS:',subs)
                                        # views                         
                                        if 'viewCount' in stats:
                                            views = int(stats['viewCount'])
                                            views /= 1000000
                                            self.youtube[1] = views
                                            print('VIEWS:',views)
                        self.grid.canvas()
                        self.grid.place_text('ytube',16,4,7)
                        self.grid.place_text('OKAY',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(500)
                        self.grid.cclear()
                    except Exception as e:
                        beeper.beep(beeppin,220,0.5)
                        print('\n-----\n')
                        print('YouTube API error.')
                        sys.print_exception(e)
                        xservers.append('YouTube')
                        self.grid.canvas()
                        self.grid.place_text('ytube',16,4,7)
                        self.grid.place_text('ERROR',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(1000)
                        self.grid.cclear()

                    # check other servers
                    for name,address in servers:
                        try:
                            self.wdt.feed()
                            print('Checking {}...'.format(name))
                            self.grid.canvas()
                            self.grid.place_text(name,16,4,7)
                            self.grid.place_text('check',16,13,7)
                            self.grid.frame_show()
                            try:
                                r = urequests.get(address)
                                status_code = r.status_code
                                r.close()
                            except:
                                status_code = 500
                            if status_code and status_code in (200,'200'):
                                pass
                            else:
                                raise ValueError('Server {} returned no usable data.'.format(name))
                            self.grid.canvas()
                            self.grid.place_text(name,16,4,7)
                            self.grid.place_text('OKAY',16,13,7)
                            self.grid.frame_show()
                            time.sleep_ms(500)
                            self.grid.cclear()
                        except Exception as e:
                            beeper.beep(beeppin,220,0.5)
                            print('\n-----\n')
                            print('Server error:',name)
                            sys.print_exception(e)
                            self.grid.canvas()
                            self.grid.place_text(name,16,4,7)
                            self.grid.place_text('ERROR',16,13,7)
                            self.grid.frame_show()
                            time.sleep_ms(1000)
                            self.grid.cclear()

                    # check weather
                    try:
                        self.wdt.feed()
                        print('Checking EZIoT Weather...')
                        self.grid.canvas()
                        self.grid.place_text('eziot',16,4,7)
                        self.grid.place_text('check',16,13,7)
                        self.grid.frame_show()
                        data = eziot.get_data(group='WEATHER',device='CLAYTON2')
                        if data:
                            rowid,epoch,gmt,ip,group,device,temp,press,hum,data4 = data[0]
                            self.weather = [temp,press,hum]
                        else:
                            raise ValueError('EZIoT returned no usable data.')
                        self.grid.canvas()
                        self.grid.place_text('eziot',16,4,7)
                        self.grid.place_text('OKAY',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(500)
                        self.grid.cclear()
                    except Exception as e:
                        beeper.beep(beeppin,220,0.5)
                        print('\n-----\n')
                        print('EZIoT error:')
                        sys.print_exception(e)
                        self.grid.canvas()
                        self.grid.place_text('eziot',16,4,7)
                        self.grid.place_text('ERROR',16,13,7)
                        self.grid.frame_show()
                        time.sleep_ms(1000)
                        self.grid.cclear()

                    # check stocks
                    print('Checking FinnHub Stock API...')
                    self.grid.canvas()
                    self.grid.place_text('stock',16,4,7)
                    self.grid.place_text('check',16,13,7)
                    self.grid.frame_show()
                    error = False
                    for name in stocks:
                        self.wdt.feed()
                        try:
                            r = urequests.get('https://finnhub.io/api/v1/quote?symbol={}&token={}'.format(name,my.finnhub_api_key))
                            data = r.content.strip()
                            r.close()                
                            if not data:
                                raise ValueError('FinnHub returned no usable data for {}.'.format(name))
                            data = json.loads(data)
                            value = 0
                            if data:
                                ##    Response Attributes:
                                ##    c
                                ##    Current price
                                ##    d
                                ##    Change
                                ##    dp
                                ##    Percent change
                                ##    h
                                ##    High price of the day
                                ##    l
                                ##    Low price of the day
                                ##    o
                                ##    Open price of the day
                                ##    pc
                                ##    Previous close price
                                value = data.get('c',0)
                                change = data.get('dp',0)
                                self.stock_values[name] = (value,change)
                            print('STOCK:',name,value,change)                              
                        except Exception as e:
                            error = True
                            beeper.beep(beeppin,220,0.5)
                            print('\n-----\n')
                            print('FinnHub API error.')
                            sys.print_exception(e)
                    self.grid.canvas()
                    self.grid.place_text('stock',16,4,7)
                    if not error:
                        self.grid.place_text('OKAY',16,13,7)
                    else:
                        self.grid.place_text('ERROR',16,13,7)
                    self.grid.frame_show()
                    time.sleep_ms(500)
                    self.grid.cclear()
                       
                    #-----------------------------------------------
                    # end check sequence
                    #-----------------------------------------------
                    
                    # clean
                    try:
                        del data
                    except:
                        pass
                    try:
                        del r
                    except:
                        pass
                    gc.collect()

            # keyboard interrupt
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                break

            # unknown exception
            except Exception as e:
                beeper.beep(beeppin,220,1)
                sys.print_exception(e)

            # disconnect
            wlan_disconnect()

#-----------------------------------------------
# start
#-----------------------------------------------

if __name__ in ('__main__','netmon2'):
    NETMON().run()

#-----------------------------------------------
# end
#-----------------------------------------------

   
