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
        time.sleep_ms(200)
        mp.scroll_text('merry'    ,16+32,3-32,16-32,3+32,True,True,'white',pause=80)
        time.sleep_ms(200)
        mp.scroll_text('merry'    ,16-32,3-32,16+32,3+32,True,True,'white',pause=80)
        time.sleep_ms(200)
        mp.scroll_text('christmas',16+64,3-0,16-64,3+0,True,True,'green',pause=60)
        time.sleep_ms(200)

        mp.scroll_text('from',16,3-32,16,3,True,True,'red',pause=80)
        mp.place_text('from',16,3,True,True,'red',write=True)
        time.sleep_ms(400)
        mp.scroll_text('from',16,3,16,3+32,True,True,'red',pause=80)
        time.sleep_ms(200)

        mp.scroll_text('me'  ,16+0,3+16,16-0,3+0,True,True,'blue',pause=80)
        mp.place_text('me'  ,16,3,True,True,'blue',write=True)
        time.sleep_ms(400)

        xes = [(random(),x) for x in range(32)]
        xes.sort()
        for junk,x in xes:
            for y in range(7):
                mp.setxy(x,y,'white',write=True)
                mp.setxy(x,y,'black',write=False)
                time.sleep_ms(12)
            mp.setxy(x,7,'white',write=True)
            time.sleep_ms(12)

        xes = [(random(),x) for x in range(32)]
        xes.sort()
        for junk,x in xes:
            for y in range(6):
                mp.setxy(x,y,'white',write=True)
                mp.setxy(x,y,'black',write=False)
                time.sleep_ms(12)
            mp.setxy(x,6,'white',write=True)
            time.sleep_ms(12)
        
        
        

        



    

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
