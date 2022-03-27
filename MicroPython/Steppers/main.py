
# imports

import time
import steppers

# set up motor

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
                   enable=21,   # enable pin
                   sleep=False, # start in sleep mode
                   sps=200,     # steps-per-second
                   smax=10240,  # max step count allowed
                   smin=-10240  # min step count allowed
                   )
s.sleepis = 1


# main function (autorun)
def test():

    try:

        while 1:
            
            print('  steps:',s.step( 100,16,sleep=True))
            time.sleep(2)

            print('  steps:',s.step(-100,16,sleep=True))
            time.sleep(2)

        

    except Exception as e:
        import sys
        sys.print_exception(e)

# test from video
def test_from_video():
    try:

        lc = 0
        
        while 1:

            lc += 1
            print('Stepper Test Loop',lc)

            s.play(s.jingle,sleep=True)
            time.sleep_ms(500)
            s.play(s.jingle2,sleep=True)
            time.sleep(1)

            s.play(s.axelf,sleep=True)
            time.sleep(1)

            s.play(s.shave,sleep=True)
            time.sleep(1)

            print('  steps:',s.step( 400,800,sleep=True))
            time.sleep(1)

            print('  steps:',s.step(-400,800,sleep=True))
            time.sleep(1)

            s.beepbeep(880,sleep=True)
            time.sleep(1)

    except Exception as e:
        import sys
        sys.print_exception(e)
        pass

# run current test
if __name__ == '__main__':
    test()

# sleep
try:
    s.sleep()
    print('sent sleep')
except:
    print('failed sleep')
    pass

