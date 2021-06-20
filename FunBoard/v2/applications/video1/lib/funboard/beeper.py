#-----------------------
# imports
#-----------------------

import time
from machine import Pin,PWM

#-----------------------
# notes
#-----------------------

# current duty cycle range for esp32 is 0 to 1023 (10 bit)

### Middle C == C4
##
##base = {'C' :16.35160,
##        'C#':17.32391,
##        'D' :18.35405,
##        'D#':19.44544,
##        'E' :20.60172,
##        'F' :21.82676,
##        'F#':23.12465,
##        'G' :24.49971,
##        'G#':25.95654,
##        'A' :27.50000,
##        'A#':29.13524,
##        'B' :30.86771,
##        }

# start of Axel F
# |d---f--d-dg-d-c-d---a--d-d|
# |a#-a-f-d-a-d^-dc-cA-e-d-----|

#-----------------------
# PWM beep class
#-----------------------

class BEEP:

    #-----------------------
    # variables
    #-----------------------

    # pin values
    pin = None # gpio number
    sink = True # pin sinks the current (i.e it's the negative)

    # sound values
    freq  = 2200 
    secs  = 0.125  # beep duration
    duty  = 25     # percent duty cycle
    vol   = 100    # percent volume (reduces duty cycle)
    wait  = secs/2 # pause between beeps
    fcps  = 100    # frequency changes per second for beep2
    root  = 440    # root frequency for play
    beat  = 0.125  # beat length for play

    # play dopixel octave colors (octaves 0-9 = at least 10 colors)
    play_colors = ('deeppink','pink','pumpkin','red','green','blue','magenta','white','white','white')

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

    def beep(self,freq=None,secs=None,vol=None,duty=None,pixel=None,color=None):
        if self.pin is not None:
            self._beep(self.pin,
                       freq or self.freq,
                       secs or self.secs,
                       vol  or self.vol ,
                       duty or self.duty,
                       pixel,color)

    def beepn(self,count=1,freq=None,secs=None,vol=None,duty=None,pixel=None,color=None,wait=None):
        if self.pin is not None:
            wait = int(1000*(wait or (secs or self.secs)/2))
            for x in range(count):
                self._beep(self.pin,
                           freq or self.freq,
                           secs or self.secs,
                           vol  or self.vol,
                           duty or self.duty,
                           pixel,color)
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

    def play(self,notestring=None,root=None,beat=None,vol=None,duty=None,dopixels=False):
        if self.pin is not None:
            self._play(self.pin,
                       notestring or self.shave_notes,
                       root or self.root,
                       beat or self.beat,
                       vol  or self.vol ,
                       duty or self.duty,
                       dopixels)

    #-----------------------
    # core functions
    #-----------------------

    def _beep(self,pin,freq=2200,secs=0.125,vol=100,duty=25,pixel=None,color=None):

        # plain beep using PWM = pure square-wave tone

        # pin = pin number to use for PWM output
        # freq = hertz integer
        # secs = beep length in seconds decimal
        # vol = percent volume
        # duty = percent on vs total cycle
        # pixel = turn on this pixel when making sound
        # color = use this color for pixel

        # duty and vol are similar
        # the true duty cycle is duty * vol
        # set duty to get max loudness for buzzer (usually at about 25%)
        # then set vol to a percentage of that to make it quieter
        # you could do everything with duty, but vol 0-100 is easier

        # catch
        try:

            # init
            #p = PWM(Pin(pin),int(freq),int(freq*(vol/100)*(duty/100)))
            p = PWM(Pin(pin),int(freq),int(1024*(vol/100)*(duty/100)))

            # wait with pixel = (index,color,...)
            if pixel != None:
                pixels.setp(pixel,color)
                time.sleep_us(int(1000000*secs))
                pixels.setp(pixel,(0,0,0))

            # wait only
            else:
                time.sleep_us(int(1000000*secs))

            # clear pin
            p.deinit()

        # any error
        except:
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
            p = PWM(Pin(pin),int(freq),duty)

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

    def _play(self,pin,notestring,root=440,beat=0.125,vol=100,duty=25,dopixels=False):

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
                    self._play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty,dopixels)
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
            self._play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty,dopixels)

    def _play_note(self,pin,note,octave,period,root,beat,vol,duty,dopixels=False):

        # catch
        try:

            freq,pixel = {
                'C' : (16.35160,7),
                'C#': (17.32391,7), # smash 3
                'D' : (18.35405,6),
                'D#': (19.44544,6), # smash 3
                'E' : (20.60172,5),
                'F' : (21.82676,4),
                'F#': (23.12465,3), # smash 3
                'G' : (24.49971,2),
                'G#': (25.95654,2), # smash 3
                'A' : (27.50000,1),
                'A#': (29.13524,1), # smash 3
                'B' : (30.86771,0)
                }.get(note,(None,None))

            period = abs(int(period))
            octave = abs(int(octave))

            if freq:
                freq *= root/440 * 2**octave
                if dopixels:
                    color = self.play_colors[min(9,octave)]
                    self._beep(pin,freq,period*beat*0.95,vol,duty,pixel,color)
                else:
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
