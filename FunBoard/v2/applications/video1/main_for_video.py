import time

# pause for editing
time.sleep_ms(4000)
 
# led on-off
led.on()
time.sleep_ms(1000)
led.off()
time.sleep_ms(1000)
led.on()
time.sleep_ms(1000)
led.off()

# pause for editing
time.sleep_ms(4000)

# led pwm
led.pwm2(0,100,10)
led.pwm2(100,0,10)
time.sleep_ms(1000)
led.pwm2(0,100,10)
led.pwm2(100,0,10)

# pause for editing
time.sleep_ms(4000)

# count binary
for x in range(1,256):
    for b in range(8):
        if x & (1<<b):
            pixels.setp(b,'green',8)
        else:
            pixels.setp(b,'off')
    time.sleep_ms(int(1000/x))
pixels.off()

# pause for editing
time.sleep_ms(4000)

# play songs
beeper.play(beeper.axelf_notes,dopixels=True)
time.sleep_ms(1000)
beeper.play(beeper.shave_notes,dopixels=True)

