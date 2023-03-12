#-----------------------
# notify
#-----------------------

# Stolen from Clayton Darwin

print('RUN: main.py')

#-----------------------
# imports
#-----------------------

import time
import _thread
from pixels import PIXELS
from wlan import STA

#-----------------------
# user setup
#-----------------------

# pixels gpio pin
pixel_pin = 14

# pixel offset
# on my clock, the first pixel is 1 right of straight up
pixel_offset = 1

# time set values
time_offset = None
timezone = 'New_York' # linux timezone string

# background color and brightness
# at this low value, only red, greem, blue work
bc = 'green'
bb = 1 

# second color and brightness
sc = 'green'
sb = 128

# minute color and brightness
mc = 'blue'
mb = 230

# hour color and brightness
hc = 'red'
hb = 192

#-----------------------
# system setup
#-----------------------

# color objects
ba = bytearray(180)
ha = bytearray(3)
ha = bytearray(3)
ha = bytearray(3)

# time set success flag
tset = False
tthread = False

#-----------------------
# main
#-----------------------

# set up pixels (global)
pixels = PIXELS(pixel_pin,60)

# loop forever
def main():

    # global var for tracking set_time thread
    global tthread

    # loop forever
    while 1:

        # catch
        try:

            # notify of loop start
            print('START main')

            # init set time
            _thread.start_new_thread(set_time,())
            tthread = True
            while tthread:
                print('TTHREAD:',tthread)
                pixels.rblink(colors=['red','green','blue','sun'],pixels=1,times=10,brightness=128,ontime=10,offtime=90)
                #pixels.run('sun',0,0)
                time.sleep_ms(1)
            pixels.run('green',0,0)           

            # default colors
            set_bgcolor()
            set_hcolor()
            set_mcolor()
            set_scolor()
            set_ccolors()

            # inner loop
            lnow = None # last now used to set time
            while 1:
                now = get_now()
                if now != lnow:
                    lnow = now
                    push_time(*now[3:]) # push takes about 4ms
                    if now[-1] == 0:
                        print('TIME:',now,tset)
                    # update time
                    if now[-2:] == (33,33):
                        if (not tset) or now[-3] == 3:
                            _thread.start_new_thread(set_time,())
                    time.sleep_ms(6)
                else:
                    time.sleep_ms(10)

        # stop
        except KeyboardInterrupt:
            break

        # error
        except Exception as e:
            import sys
            sys.print_exception(e)
            print('ERROR: main')
            for x in range(3):
                pixels.run('red',0,0)

        # clean up
        finally:
            pixels.off()

        # wait
        print('PAUSE: restart main in 4 secs')
        time.sleep_ms(4000)

#-----------------------
# aux functions
#-----------------------

# background color 
def set_bgcolor(color=None,brightness=None):
    color = color or bc
    brightness = brightness or bb
    r,g,b = pixels.make_color(color,brightness)
    global ba
    ba = bytearray((g,r,b)*60)

# hour hand color
def set_hcolor(color=None,brightness=None):
    color = color or hc
    brightness = brightness or hb
    global ha
    ha = pixels.make_color(color,brightness)
    
# minute hand color
def set_mcolor(color=None,brightness=None):
    color = color or mc
    brightness = brightness or mb
    global ma
    ma = pixels.make_color(color,brightness)
    
# second hand color
def set_scolor(color=None,brightness=None):
    color = color or sc
    brightness = brightness or sb
    global sa
    sa = pixels.make_color(color,brightness)

# combined minute-hour hand
def set_ccolors():
    global hmsa,hma,hsa,msa
    hmsa = tuple([min(255,a+b+c) for a,b,c in zip(ha,ma,sa)])
    hma  = tuple([min(255,a+b  ) for a,b   in zip(ha,ma   )])
    hsa  = tuple([min(255,a+b  ) for a,b   in zip(ha,sa   )])
    msa  = tuple([min(255,a+b  ) for a,b   in zip(ma,sa   )])

# current local (year,month,day,hour,minute,second)
# this accounts for offset
def get_now():
    return time.gmtime(time.time()+(time_offset*3600))[:6]

# push (set) time on pixels
def push_time(h,m,s):
    # correct to 12-hour clock
    if h >= 12:
        h -= 12
    # 60 pixels / 12 hours = 5 pixels per hour
    # 5 * minutes/60 == minutes/12 = add on for % minute
    h = h*5 + int(m/12)
    # if pixels don't start at straight-up position
    h = (h or 60) - pixel_offset
    m = (m or 60) - pixel_offset
    s = (s or 60) - pixel_offset

    # set background
    pixels.np.buf = ba[:]

    # select colors
    if h == m == s:
        hc = hmsa
        mc = hmsa
        sc = hmsa
    elif h == m:
        hc = hma
        mc = hma
        sc = sa
    elif h == s:
        hc = hsa
        mc = ma
        sc = hsa
    elif m == s:
        hc = ha
        mc = msa
        sc = msa
    else:
        hc = ha
        mc = ma
        sc = sa

    # quick set
    pixels.setp(h,hc)
    pixels.setp(m,mc)
    pixels.setp(s,sc)

    # write
    pixels.write()   

# update time from internet
def set_time():
    # globals
    global tset,time_offset,tthread
    # clear on init
    tset = False
    # simple handling of day changes
    hour,minute = time.gmtime()[3:5]
    if (hour == 23 and minute >= 56):
        return False
    # wifi connect
    wlan = STA()
    wlan.connect()
    # set rtc
    tset = wlan.set_rtc(only_if_needed=False)
    print('RTC UPDATE:',tset)
    # get time offset if needed
    if tset and time_offset == None:
        import urequests as ur
        hour = None
        for x in range(10):
            try:
                # no guarantee this will stay valid
                hour = int(ur.get('http://claytondarwin.com/cgi-bin/ztime.py?TZ={}'.format(timezone)).text.split()[3])
                print('LOCAL HOUR:',hour)
                time_offset = hour - time.gmtime()[3]
                if time_offset > 12:
                    time_offset -= 24
                elif time_offset < -12:
                    time_offset += 24
                break
            except:
                print('LOCAL HOUR: XX')
                wlan.disconnect()
                time.sleep_ms(100)
                wlan.connect()
                time.sleep_ms(100)
        del ur
        print('LOCAL RTC OFFSET:',time_offset)
    # kill wifi
    wlan.disconnect()
    del wlan
    # done
    tthread = False
    print('RTC DONE:',tthread)
    return tset

#-----------------------
# run on start
#-----------------------

if __name__ == "__main__":
    main()
    
#-----------------------
# end
#-----------------------
