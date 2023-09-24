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
from pixels import PIXELS
from random import randint, choice

#-----------------------
# testing catch
#-----------------------

try:

    global np
    np = PIXELS(21,64)

    pc = 64 # pixel count
    ap = 8  # active pixels
    bm = 64 # max brightness
    pd = [] # pixel data (index,color_name,brightness_percent)
    lt = 100 # loop time (wait at end)
    lc = 0  # loop count
    ac = int(200/ap) # active count (when to add a new pixel)
    cc = [x for x in np.colors(True) if x not in ('off','black','white')] # color choices

    while 1:

        # add a new pixel
        if not lc % ac:
            up = [x[0] for x in pd]
            uc = [x[1] for x in pd]
            p = randint(0,pc-1)
            while p in up:
                p = randint(0,pc-1)
            c = choice(cc)
            while c in uc:
                c = choice(cc)
            pd.append([p,c,0])
            print('ADD:',[p,c])

        # update all pixels
        for x in range(len(pd)):
            p,c,b = pd[x]
            b += 1
            pd[x][2] = b
            if b > 200:
                continue
            elif b > 100:
                b = 200-b
            b = bm * (b/100)
            np.setp(p,c,b)
        np.write()

        # remove dead pixels
        while pd and pd[0][2] >= 200:
            print('POP:',pd.pop(0)[:2])

        # adjust counts
        lc += 1
        if lc >= 200:
            lc = 0

        # pause
        time.sleep_ms(lt)
        
    

    

    

    





    
    

    

#-----------------------
# end testing catch
#-----------------------

except KeyboardInterrupt:
    print('Keyboard Interrupt: main.py ending.')
    
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Exception: main.py ending.')

finally:
    try:
        np.off()
    except:
        pass

#-----------------------
# end
#-----------------------
