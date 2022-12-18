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

#-----------------------
# main
#-----------------------

# main
def main():

    # set up pixels (global)
    pixels = PIXELS(pixel_pin,pixel_count)
    pixels.run(color='red',brightness=brightness,ontime=10,offtime=0)
    pixels.off()

    # for later use
    r = pixels.make_color('red',int(brightness/2))
    g = pixels.make_color('green',int(brightness/2))
    z = (0,0,0)

    # loop
    while 1:

        # flash about 10 seconds
        pixels.rblink('red green sun'.split(),pixels=4,times=222,brightness=brightness,ontime=44,offtime=0)
        pixels.off()

        # follow
        for x in range(0,pixel_count,10):
            pixels.np[x] = r
        for x in range(5,pixel_count,10):
            pixels.np[x] = g
        pixels.np.write()
        for x in range(int(pixel_count/4)):
            end = pixels.np.buf[-3:]
            pixels.np.buf = end + pixels.np.buf[:-3]
            pixels.np.write()
            time.sleep_ms(100)
        for x in range(int(pixel_count/4)):
            end = pixels.np.buf[:3]
            pixels.np.buf = pixels.np.buf[3:]+end
            pixels.np.write()
            time.sleep_ms(100)
        pixels.off()

        # run 2 directions
        for x in range(pixel_count):
            pixels.np[x] = r
            pixels.np[pixel_count-1-x] = g
            pixels.np.write()
            time.sleep_ms(10)
            pixels.np[x] = z
            pixels.np[pixel_count-1-x] = z
            pixels.np.write()            
        pixels.off()

#-----------------------
# run on start
#-----------------------

if __name__ == "__main__":
    main()
    
#-----------------------
# end
#-----------------------
