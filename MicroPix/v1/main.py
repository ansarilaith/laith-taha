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

    mp = micropix.MicroPix(21,2,2)
    mp.set_bright(8)
    mp.make_xy2it()

    def snow(colors=['white'],
             loops=-1,
             depth=3,
             layers=2,
             speed=16,
             melt=True):

        # get colors
        black = mp.get_color('black')
        colors = [mp.get_color(c) for c in colors]
        clen = len(colors)

        # loop prep
        cols = [0]*mp.pixelx
        flakes = mp.pixelx*depth
        history = []

        # main loop
        while loops:
            loops -= 1

            # select color
            if clen == 1:
                color = colors[0]
            while 1:
                color = colors[randint(0,clen-1)]
                if color not in history:
                    break
            history.append(color)
            history = history[-layers:]

            # color loop
            for f in range(flakes):

                # snow
                x = randint(0,mp.pixelx-1)
                if x != 0 and cols[x] - cols[x-1] > 1:
                    x -= 1
                elif x != mp.pixelx-1 and cols[x] - cols[x+1] > 1:
                    x += 1
                d = cols[x] # depth in col
                if d < mp.pixely:
                    f = mp.pixelx-1-d # fall distance
                    for y in range(f):
                        mp.setxy(x,y,color,cfixed=True,write=True)
                        mp.setxy(x,y,black,cfixed=True,write=False)
                        time.sleep_ms(speed)
                    mp.setxy(x,f,color,cfixed=True,write=True)
                    cols[x] += 1
                    time.sleep_ms(speed)

                # melt
                if melt:

                    # select old colors for deletion
                    xs = []
                    for x in range(mp.pixelx):
                        c = mp.geti(mp.xy2i(x,mp.pixely-1))
                        if (c != black) and (c not in history):
                            xs.append(x)
                    if xs:
                        x = xs[randint(0,len(xs)-1)]
                        depth = cols[x]
                        for y in range(mp.pixely-1,mp.pixely-depth-1,-1):
                            color2 = mp.geti(mp.xy2i(x,y))
                            mp.setxy(x,y+1,color2,cfixed=True,write=False)
                        mp.setxy(x,mp.pixely-depth,black,cfixed=True,write=False)
                        cols[x] -= 1
                        mp.write()
                        time.sleep_ms(speed)

    colors = ['green', 'greener', 'lime', 'chartreuse', 'yellow', 'sunflower', 'orange', 'pumpkin', 'tomato', 'red', 'rose', 'fuchsia', 'magenta', 'pinker', 'pink', 'violet', 'ultra', 'indigo', 'blue', 'water', 'sky', 'azure', 'cyan', 'aqua', 'mint', 'grass']

##    while 1:
##        for c in ['red','blue','green']:
##            mp.setxy(15,15,c,write=True)
##            time.sleep_ms(100)
##            mp.setxy(15,15,'black',write=True)
##            time.sleep_ms(100)



    snow(colors)

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
