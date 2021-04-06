
import time,sys
import gpio_leds

np = gpio_leds.NP(21,64)
np.set_brightness(8)
np.off()

time.sleep_ms(4000)

try:
    while 1:
        for color in 'red green blue'.split():
            colorvalues = np.get_color(color)
            for pixel in range(np.pixels):
                np.np[pixel] = colorvalues
                np.np.write()
                time.sleep_ms(100)
                np.np[pixel] = (0,0,0)
                np.np.write()
                
except KeyboardInterrupt:
    np.off()

##try:
##
##    for color in 'red green blue white'.split():
##
##        for level in (2,4,8,16,32,64,128,255):
##
##            np.set_brightness(level)
##            colorvalues = np.get_color(color)
##            print(color.upper(),level)
##
##            for pixel in range(np.pixels):
##                np.np[pixel] = colorvalues
##            np.np.write()
##
##            beeper.beep()
##
##            time.sleep_ms(3000)
##            np.off()
##            time.sleep_ms(1000)
##
##except Exception as e:
##    sys.print_exception(e)
        
np.off()

print()
print('DONE')



