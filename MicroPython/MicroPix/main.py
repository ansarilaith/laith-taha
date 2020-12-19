#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# general imports
#-----------------------

import os
import sys
import time

#-----------------------
# testing catch
#-----------------------

try:

    #-----------------------
    # micropix examples
    #-----------------------

    import micropix
    from urandom import random,randint

    mp = micropix.MicroPix(21,4,1)
    mp.set_bright(8)

    while 1:

        mp.clear()
        time.sleep_ms(250)
        mp.scroll_text('merry',16+32,3-32,16-32,3+32,True,True,'white',pause=80)
        time.sleep_ms(250)
        mp.scroll_text('merry',16-32,3-32,16+32,3+32,True,True,'white',pause=80)
        time.sleep_ms(250)
        mp.scroll_text('christmas',16+64,3,16-64,3,True,True,'green',pause=60)
        time.sleep_ms(250)

        mp.scroll_text('to',16,3-32,16,3,True,True,'red',pause=80)
        mp.place_text('to',16,3,True,True,'red',write=True)
        time.sleep_ms(500)
        mp.scroll_text('to',16,3,16,3+32,True,True,'red',pause=80)
        time.sleep_ms(250)

        mp.scroll_text('you',16,3+16,16,3,True,True,'blue',pause=80)
        mp.place_text('you' ,16,3,True,True,'blue',write=True)
        time.sleep_ms(500)

        # clear with snow (one in each col)
        cols = [(random(),x) for x in range(32)]
        cols.sort()
        for _,x in cols:
            for y in range(7):
                mp.setxy(x,y,'white',write=True)
                mp.setxy(x,y,'black',write=False)
                time.sleep_ms(12)
            mp.setxy(x,7,'white',write=True)
            time.sleep_ms(12)

        # then do random snow
        flakes = 64
        cols = [1]*32
        while flakes:
            x = randint(0,31)
            if x != 0 and cols[x] - cols[x-1] > 1:
                x -= 1
            elif x != 31 and cols[x] - cols[x+1] > 1:
                x += 1
            d = cols[x] # depth in col
            if d < 8:
                f = 7-d # fall distance
                for y in range(f):
                    mp.setxy(x,y,'white',write=True)
                    mp.setxy(x,y,'black',write=False)
                    time.sleep_ms(12)
                mp.setxy(x,f,'white',write=True)
                cols[x] += 1
                time.sleep_ms(12)
                flakes -= 1

#-----------------------
# end testing catch
#-----------------------

except KeyboardInterrupt:
    print('Keyboard Interrupt: main.py ending.')
    
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Exception: main.py ending.')

#-----------------------
# end
#-----------------------
