#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: main.py')

#-----------------------
# imports
#-----------------------

import time
from machine import Pin
import device_rylr998

#-----------------------
# run options
#-----------------------

def run():
    send() # for mobile ESP32
    #bounce() # for base ESP32

#-----------------------
# message bounce object
#-----------------------

# listen and send back messages

class BOUNCER:

    def __init__(self,network=18,address=1,power=22):

        self.lora = device_rylr998.RYLR998(network,address,power)

    def loop(self):

        while 1:
            
            line = self.lora.readline()

            if not line:
                time.sleep_ms(100)

            else:
                Pin(2,Pin.OUT,value=1)
                print()
                print('LINE IN:',line)
                if line.startswith('+RCV'):
                    line = self.lora.rcvparse(line)
                    print('  SEND:',line['addr'],line['data'],self.lora.send(line['addr'],line['data']))
                Pin(2,Pin.OUT,value=0)

def bounce():
    b = BOUNCER()
    b.loop()
            
#-----------------------
# message sender object
#-----------------------

# send messages, check responses

class SENDER:

    def __init__(self,network=18,address=2,power=22):

        self.lora = device_rylr998.RYLR998(network,address,power)
        

    def loop(self):

        loops = 0
        stack = []

        while 1:

            # notify
            loops += 1
            print('LOOP:',loops)

            # match line in to last sent message
            for line in self.lora.readlines():
                print('  LINE IN:',line)
                if line.startswith('+RCV'):
                    line = self.lora.rcvparse(line)
                    sent = self.lora.sent()
                    recv = [line['addr'],line['dlen'],line['data']]
                    print('    SENT:',sent)
                    print('    RECV:',recv)
                    if sent == recv:
                        print('    MATCH: True')
                        # flash blue LED
                        Pin(2,Pin.OUT,value=1)
                        time.sleep_ms(100)
                        Pin(2,Pin.OUT,value=0)

            # send new message
            message = 'Hello from loop {}.'.format(loops)
            print('  SEND:',1,message,self.lora.send(1,message))

            # wait a while
            time.sleep_ms(1000)


def send():
    s = SENDER()
    s.loop()

#-----------------------
# self run
#-----------------------

run()

#-----------------------
# end
#-----------------------
