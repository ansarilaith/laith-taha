import time
import steppers

##s = steppers.HBRIDGE(5,18,19,23,   # A,a,B,b
##                     mode=3,       # see modes above
##                     reverse=False,# reverse motor default direction
##                     invert=False, # invert all mode pin states
##                     sleep=False,  # start in sleep mode
##                     sps=200,      # steps-per-second
##                     smax=10240,   # max step count allowed
##                     smin=-10240   # min step count allowed
##                     )

s = steppers.A4899(18,          # step
                   19,          # direction
                   enable=5,    # enable pin
                   sleep=False, # start in sleep mode
                   sps=200,     # steps-per-second
                   smax=10240,  # max step count allowed
                   smin=-10240  # min step count allowed
                   )



try:

    lc = 0
    
    while 1:

        lc += 1
        print(lc)

        s.play(s.jingle,sleep=True)
        time.sleep(1)
        s.play(s.jingle2,sleep=True)
        time.sleep(1)

        s.play(s.axelf,sleep=True)
        time.sleep(1)

        s.play(s.shave,sleep=True)
        time.sleep(1)

        s.step(400,800)
        time.sleep(1)

        s.step(-400,800,sleep=True)
        time.sleep(1)

        s.beepbeep(880,sleep=True)

except Exception as e:
    import sys
    sys.print_exception(e)
    pass

s.sleep()




##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(110,10,sleep=True)
##    print('TIME 10:',s.steps,time.ticks_diff(time.ticks_ms(),t1),)
##
##    time.sleep(2)
##    
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(-110,10,sleep=True)
##    print('TIME 10:',s.steps,time.ticks_diff(time.ticks_ms(),t1))
##
##    time.sleep(2)
    
    
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(100,100)
##    print('TIME  100:',time.ticks_diff(time.ticks_ms(),t1))
##    
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(-100,100)
##    print('TIME  100:',time.ticks_diff(time.ticks_ms(),t1))
##    
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(1000,1000)
##    print('TIME 1000:',time.ticks_diff(time.ticks_ms(),t1))
##
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(-1000,1000)
##    print('TIME 1000:',time.ticks_diff(time.ticks_ms(),t1))
##
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(2000,2000)
##    print('TIME 2000:',time.ticks_diff(time.ticks_ms(),t1))
##
##    s.last = time.ticks_us()
##    t1=time.ticks_ms()
##    s.step(-2000,2000)
##    print('TIME 2000:',time.ticks_diff(time.ticks_ms(),t1))
##
##    s.zero()
