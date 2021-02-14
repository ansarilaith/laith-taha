
import time
import gpio_leds

np = gpio_leds.NP(21,64)

np.off()

time.sleep_ms(4000)

for color in 'red green blue white'.split():

    for level in (2,4,8,16,32,64,128,255):

        np.set_brightness(level)
        colorvalues = np.get_color(color)
        print(color.upper(),level)

        for pixel in range(np.pixels):
            np.np[pixel] = colorvalues
        np.np.write()

        beeper.beep()

        time.sleep_ms(3000)
        np.off()
        time.sleep_ms(1000)
        
np.off()

print()
print('DONE')



