# beeper.py
# Copyright (c) 2019 Clayton Darwin
# symple.design/clayton claytondarwin@gmail.com

# notify
print('LOAD: beeper.py')

import time
from machine import Pin,PWM

# plain beep using PWM = pure square-wave tone
def beep(pin=12,freq=2200,secs=0.1,duty=33.33):

    # catch
    try:

        p = PWM(Pin(pin),freq=int(freq),duty=int(freq*(duty/100)))
        time.sleep_us(int(1000000*secs))
        p.deinit()

    # any error
    except:
        try:
            p.deinit()
        except:
            pass

# step between two frequencies using PWM
# this works well for short sounds and/or large steps
# there is an audible jump between steps
def beep2(pin=12,freq1=2200,freq2=4400,secs=0.1,duty=33.33,sps=100):

    steps = secs*sps
    stepperiod = int(1000000*secs/steps)
    stepchange = (freq2-freq1)/steps

    duty = int(freq1*(duty/100))

    p = PWM(Pin(pin),freq=int(freq1),duty=duty)

    # catch
    try:

        # loop
        for x in range(steps):
            p.freq(int(freq1+x*stepchange))
            time.sleep_us(stepperiod)

    # any error
    except:
        pass

    # clear pin
    p.deinit()
    
# more complex, doesn't use native PWM
# has better sound quality for longer sounds? not sure
def beep3(pin=12,freq1=2200,freq2=4400,secs=0.1,duty=33.33):

    # use milliseconds to track the beep length
    # use microseconds to handle the on-off periods
    # seconds are not accurate enough
    # microseconds are very process intensive after clock turns over

    # frequencies
    freq1 = max(1,freq1)
    if not freq2:
        freq2 = freq1
    else:
        freq2 = max(1,freq2)

    # frequency change
    fc = freq2-freq1

    # duration milliseconds
    duration = int(secs*1000)

    # duty factor
    onduty = duty/100.0
    offduty = 1-onduty

    # instantiate pin
    p = Pin(pin,Pin.OUT)

    # catch
    try:

        # start time
        starttime = time.ticks_ms()
        last = 0

        # loop
        while 1:

            # time since start milliseconds
            sincestart = time.ticks_diff(time.ticks_ms(),starttime)

            # time is up
            if sincestart >= duration:
                break

            # current cycle period in microseconds (better resolution)
            period = 1000000 / (freq1 + fc * sincestart/duration)

            # on
            p.value(1)
            time.sleep_us(int(period*onduty))

            # off
            p.value(0)
            time.sleep_us(int(period*offduty))
            
    # any error
    except:
        pass

    # clear pin
    p.value(0)
    Pin(pin,Pin.IN)
            

def axelf(pin=12,root=220,beat=0.125):

    # start of Axel F
    # |d---f--d-dg-d-c-d---a--d-d|
    # |a#-a-f-d-a-D-dc-ca-e-d-----|

    notes = [

    (146.833,4), # d
    (174.614,3), # f
    (146.833,2), # d
    (146.833,1), # d
    (195.998,2), # g
    (146.833,2), # d
    (138.591,2), # c

    (146.833,4), # d
    (220.000,3), # a
    (146.833,2), # d
    (146.833,1), # d
    (233.082,2), # a#
    (220.000,2), # a
    (174.614,2), # f

    (146.833,2), # d
    (220.000,2), # a
    (293.665,2), # dd
    (146.833,1), # d
    (138.591,2), # c
    (138.591,1), # c
    (110.000,2), # A
    (164.814,2), # e
    (146.833,6), # d

    ]

    root = root/220

    for freq,period in notes:
        beep(pin,freq*root,period*beat)

        


            


















