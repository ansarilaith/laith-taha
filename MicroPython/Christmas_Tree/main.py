#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# imports
#-----------------------

import time
from pixels import PIXELS

#-----------------------
# user setup
#-----------------------

# pixels gpio pin
pixel_pin = 14

# pixels on string
pixel_count = 139

# brightness percent
brightness = 32

gran = 2
start = 16
stop = 76
hold = 60
at_z = 6 # wait periods at zero


#-----------------------
# pixels
#-----------------------

# set up pixels (global)
pixels = PIXELS(pixel_pin,pixel_count)
pixels.off()
print('PIXELS READY')

# fixed colors for later use
r = pixels.make_color('red',int(brightness/2))
g = pixels.make_color('green',int(brightness/2))
z = (0,0,0)

def load():
    for x in range(0,pixel_count,10):
        pixels.np[x] = r
        pixels.np.write()
        time.sleep_ms(3)
    for x in range(5,pixel_count,10):
        pixels.np[x] = g
        pixels.np.write()
        time.sleep_ms(3)

def up1():
    end = pixels.np.buf[-3:]
    pixels.np.buf = end + pixels.np.buf[:-3]
    pixels.np.write()

def down1():
    end = pixels.np.buf[:3]
    pixels.np.buf = pixels.np.buf[3:]+end
    pixels.np.write()

#-----------------------
# main
#-----------------------

def main():

    # loop
    while 1:

        # flash about 4 seconds
        print('PIXELS FLASH')
        pixels.rblink('red green sun'.split(),pixels=4,times=91,brightness=brightness,ontime=44,offtime=0)
        pixels.off()
        
        # base load
        load()
        for X in range(4):
            print('UP',X+1)
            # accelerate up
            for x in range(start,stop+1):
                t = int(gran*1000/x)
                up1()
                time.sleep_ms(t)
            # hold up
            for x in range(hold):
                up1()
                time.sleep_ms(t)
            # decelerate up
            for x in range(stop,start-1,-1):
                t = int(gran*1000/x)
                up1()
                time.sleep_ms(t)
            # pause at 0
            time.sleep_ms(t*at_z)
            print('DOWN',X+1)
            # accelerate down
            for x in range(start,stop+1):
                t = int(gran*1000/x)
                down1()
                time.sleep_ms(t)
            # hold down
            for x in range(hold):
                down1()
                time.sleep_ms(t)
            # decelerate down
            for x in range(stop,start-1,-1):
                t = int(gran*1000/x)
                down1()
                time.sleep_ms(t)
            # pause at 0
            time.sleep_ms(t*at_z)
        pixels.off()

        



### 2nd version of main
### same as 1st, but longer periods
##def main2():
##
##    # set up pixels (global)
##    pixels = PIXELS(pixel_pin,pixel_count)
##    pixels.off()
##    print('PIXELS READY')
##
##    # fixed colors for later use
##    r = pixels.make_color('red',int(brightness/2))
##    g = pixels.make_color('green',int(brightness/2))
##    z = (0,0,0)
##
##    # run 2 directions
##    print('PIXELS R-G RUN')
##    for x in range(pixel_count):
##        pixels.np[x] = r
##        pixels.np[pixel_count-1-x] = g
##        pixels.np.write()
##        time.sleep_ms(10)
##        pixels.np[x] = z
##        pixels.np[pixel_count-1-x] = z
##        pixels.np.write()            
##    pixels.off()
##
##    # loop
##    while 1:
##
##        # flash about 4 seconds
##        print('PIXELS FLASH')
##        pixels.rblink('red green sun'.split(),pixels=4,times=91,brightness=brightness,ontime=44,offtime=0)
##        pixels.off()
##
##        # follow up for about 26 seconds
##        print('PIXELS RUN UP')
##        for x in range(0,pixel_count,10):
##            pixels.np[x] = r
##        for x in range(5,pixel_count,10):
##            pixels.np[x] = g
##        pixels.np.write()
##        for x in range(260):
##            end = pixels.np.buf[-3:]
##            pixels.np.buf = end + pixels.np.buf[:-3]
##            pixels.np.write()
##            time.sleep_ms(100)
##        pixels.off()
##
##        # flash about 4 seconds
##        print('PIXELS FLASH')
##        pixels.rblink('red green sun'.split(),pixels=4,times=91,brightness=brightness,ontime=44,offtime=0)
##        pixels.off()
##
##        # follow down for about 26 seconds
##        print('PIXELS RUN DOWN')
##        for x in range(0,pixel_count,10):
##            pixels.np[x] = r
##        for x in range(5,pixel_count,10):
##            pixels.np[x] = g
##        pixels.np.write()
##        for x in range(260):
##            end = pixels.np.buf[:3]
##            pixels.np.buf = pixels.np.buf[3:]+end
##            pixels.np.write()
##            time.sleep_ms(100)
##        pixels.off()

#-----------------------
# run on start
#-----------------------

if __name__ == "__main__":
    main()
    
#-----------------------
# end
#-----------------------
