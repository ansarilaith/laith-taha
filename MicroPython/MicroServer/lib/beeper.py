#-----------------------
# notify
#-----------------------

print('LOAD: gpio_beep.py')

#-----------------------
# imports
#-----------------------

import time
from machine import Pin,PWM


#-----------------------
# smaller beep class
#-----------------------

class MINIBEEP:
    # plain beep using PWM = pure square-wave tone
    # duty and vol are similar
    # the true duty cycle is duty * vol
    # set duty to get max loudness for buzzer (usually at about 25%)
    # then set vol to a percentage of that to make it quieter
    # you could do everything with duty, but vol 0-100 is easier

    # sound values
    freq = 2200 
    msecs = 125 # beep duration
    count = 1 # how many beeps
    wait = int(msecs/2) # pause between beeps
    duty = 25 # percent duty cycle
    vol = 100 # percent volume (reduces duty cycle)

    def __init__(self,pin):       
        self.pin = pin

    def beep(self,pin=None,freq=None,msecs=None,count=1,wait=None,vol=None,duty=None):
        for x in range(count or self.count):
            p = PWM(Pin(pin or self.pin),freq=freq or self.freq,duty=0)
            time.sleep_ms(10)
            p.duty_u16(int(65535*((vol or self.vol)/100)*((duty or self.duty)/100)))
            #p = PWM(Pin(pin or self.pin),freq=freq or self.freq,duty=int(1023*((vol or self.vol)/100)*((duty or self.duty)/100)))
            time.sleep_ms(msecs or self.msecs)
            p.duty_u16(0)
            p.deinit()
            time.sleep_ms(wait or self.wait)

#-----------------------
# full beep class
#-----------------------

class BEEP:

    #-----------------------
    # variables
    #-----------------------

    # pin values
    pin = None # gpio number

    # sound values
    freq  = 2200 
    secs  = 0.125  # beep duration
    duty  = 25     # percent duty cycle
    vol   = 100    # percent volume (reduces duty cycle)
    wait  = secs/2 # pause between beeps
    fcps  = 100    # frequency changes per second for beep2
    root  = 440    # root frequency for play
    beat  = 0.125  # beat length for play

    # note strings
    jingle_notes = 'e5 g5 b5 d6 p d5'
    jingle2_notes = 'd7'
    shave_notes  = 'c4 p g3 g3 a32 g32 p p b3 p c4'
    axelf_notes  = 'd44 f43 d42 d41 g42 d42 c42 d44 a43 d42 d41 a#42 a42 f42 d42 a42 d52 d41 c42 c41 a32 e42 d46' # required for smash 3
 
    #-----------------------
    # init
    #-----------------------

    # init with gpio pin number
    def __init__(self,pin):
        self.pin = abs(int(pin))

    #-----------------------
    # beep functions
    #-----------------------

    def beep(self,freq=None,secs=None,vol=None,duty=None):
        if self.pin is not None:
            self._beep(self.pin,
                       freq or self.freq,
                       secs or self.secs,
                       vol  or self.vol ,
                       duty or self.duty)

    def beepn(self,count=1,wait=None,freq=None,secs=None,vol=None,duty=None):
        if self.pin is not None:
            wait = int(1000*(wait or (secs or self.secs)/2))
            for x in range(count):
                self._beep(self.pin,
                           freq or self.freq,
                           secs or self.secs,
                           vol  or self.vol,
                           duty or self.duty)
                time.sleep_ms(wait)

    def beep2(self,freq=None,freq2=None,secs=None,vol=None,duty=None,fcps=100):
        if self.pin is not None:
            self._beep2(self.pin,
                        freq  or self.freq,
                        freq2 or freq*2,
                        secs  or self.secs,
                        vol   or self.vol ,
                        duty  or self.duty,
                        fcps  or self.fcps)

    def play(self,notestring=None,root=None,beat=None,vol=None,duty=None):
        if self.pin is not None:
            self._play(self.pin,
                       notestring or self.shave_notes,
                       root or self.root,
                       beat or self.beat,
                       vol  or self.vol ,
                       duty or self.duty)

    #-----------------------
    # core functions
    #-----------------------

    def _beep(self,pin,freq=2200,secs=0.125,vol=100,duty=25):

        # plain beep using PWM = pure square-wave tone

        # pin = pin number to use for PWM output
        # freq = hertz integer
        # secs = beep length in seconds decimal
        # vol = percent volume
        # duty = percent on vs total cycle

        # duty and vol are similar
        # the true duty cycle is duty * vol
        # set duty to get max loudness for buzzer (usually at about 25%)
        # then set vol to a percentage of that to make it quieter
        # you could do everything with duty, but vol 0-100 is easier

        # catch
        try:

            # init
            duty = int(65535*(vol/100)*(duty/100))
            p = PWM(Pin(pin),freq=int(freq),duty_u16=duty)
            #p = PWM(Pin(pin),freq=int(freq),duty=int(freq*(vol/100)*(duty/100)))
            #p = PWM(Pin(pin),freq=int(freq),duty=int(1024*(vol/100)*(duty/100)))

            # wait
            time.sleep_us(int(1000000*secs))

            # clear pin
            p.duty_u16(0)
            p.deinit()
            
        # any error
        except Exception as e:
            print('ERROR')
            import sys
            sys.print_exception(e)
            try:
                p.deinit()
            except:
                pass
             
    def _beep2(self,pin,freq=2200,freq2=4400,secs=0.125,vol=100,duty=25,fcps=100):

        # move between two frequencies using PWM
        # this works well for short sounds and/or large steps
        # there is an audible jump between steps

        # see the notes in beep()
        # fcps = freq changes per second, how many frequency changes to make per second

        # catch
        try:

            # vars
            steps = secs*fcps
            stepperiod = int(1000000*secs/steps)
            stepchange = (freq2-freq)/steps
            duty = int(1024*(vol/100)*(duty/100))

            # init
            p = PWM(Pin(pin),freq=int(freq),duty=duty)

            # loop
            for x in range(steps):
                p.freq(int(freq+x*stepchange))
                time.sleep_us(stepperiod)

            # clear pin
            p.deinit()

        # any error
        except:
            try:
                p.deinit()
            except:
                pass

    def _play(self,pin,notestring,root=440,beat=0.125,vol=100,duty=25):

        # notestring = any string of a note+optional_sharp+octave+beats sequences
        # only "ABCDEFGP#0123456789" characters matter, others ignored
        # example: "d44" == "D44" == "d 4 4" == "d, 4, 4" == "D4-4"
        # example: "d44 a43 d42 d41 a#42 a42 f42"
        # example: "d44a43d42d41a#42a42f42"

        # middle C for 3 beats = 'C43'
        # a pause for 3 beats = 'P3' or 'P03'

        # upper case
        notestring = notestring.upper()

        # all strings
        note,octave,period = '','',''

        for c in notestring:

            # note
            if c in 'ABCDEFGP':
                if note:
                    self._play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty)
                    octave,period = '',''
                note = c

            # sharp
            elif c == '#' and note:   # required for smash 3
                note += '#'           # required for smash 3

            # digit
            elif c.isdigit():

                # period
                if octave or note == 'P':
                    period += c

                # octave
                else:
                    octave = c

            # junk
            else:
                pass

        # last note
        if note:
            self._play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty)

    def _play_note(self,pin,note,octave,period,root,beat,vol,duty):

        # catch
        try:

            freq = {
                'C' : 16.35160,
                'C#': 17.32391, # smash 3
                'D' : 18.35405,
                'D#': 19.44544, # smash 3
                'E' : 20.60172,
                'F' : 21.82676,
                'F#': 23.12465, # smash 3
                'G' : 24.49971,
                'G#': 25.95654, # smash 3
                'A' : 27.50000,
                'A#': 29.13524, # smash 3
                'B' : 30.86771
                }.get(note,None)

            period = abs(int(period))
            octave = abs(int(octave))

            if freq:
                freq *= root/440 * 2**octave
                self._beep(pin,freq,period*beat*0.95,vol,duty)
                time.sleep_ms(int(period*beat*50))

            else:
                time.sleep_ms(int(period*beat*1000))

        # any error
        except Exception as e:
            import sys
            sys.print_exception(e)

#-----------------------
# end
#-----------------------
