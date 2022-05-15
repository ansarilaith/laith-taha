#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: device_rylr998.py')

#-----------------------
# imports
#-----------------------

import time
from machine import UART
from machine import Pin

#-----------------------
# main class
#-----------------------

# this is an example of what you might need, but...
# there are many extra functions that probably won't be needed
# comment out (or delete) the ones that are not needed

class RYLR998:

    #-----------------------
    # common user variables
    #-----------------------

    # these change between devices (frequently)
    # call update() if changed after __init__()

    # device network and adress
    at_ad =  1 # <network address> 0-65535
    at_id = 18 # <netwirk id> 3-15 or 18 default 18

    # RF power
    at_rf = 22 # <rf power> 0-22 default 22

    #-----------------------
    # other user variables
    #-----------------------

    # these typically don't change much
    # call update() if changed after init

    # GPIO pins used for uart and reset
    reset_pin = 18 # pin used for hard reset
    uart_rx   = 16 # pin used for ESP32 RX <-- RYLR988 TX
    uart_tx   = 17 # pin used for ESP32 TX --> RYLR988 RX

    # RF frequency
    at_bd = 915000000 # <band> 470000000, 868500000, 915000000

    # parameter values
    at_sp =  9 # <Spreading Factor> 7-11 default 9
    at_bw =  7 # <Bandwidth> 7-9 default 7 
    at_cr =  1 # <Coding Rate> 1-4 default 1
    at_pp = 12 # <Programmed Preamble> 12 default 12 (can be 4-24 if net id is 18)

    #-----------------------
    # system variables
    #-----------------------

    # don't change these
    port = None
    buffer = b''

    # uart storage sizes
    uart_tx_buf = 256 # >128 required by upython
    uart_rx_buf = 512 # this should be plenty

    # adds text to numeric error messages
    errors = {'1':'No line end (\\r\\n).',
              '2':'No line head (AT).',
              '4':'Unknown command.',
              '5':'Data length error.',
              '10':'TX timeout.',
              '12':'CRC error.',
              '13':'TX > 240 bytes.',
              '14':'Flash write error.',
              '15':'Unknown error.',
              '17':'Last TX failed.',
              '18':'Preamble value not allowed.',
              '19':'RX failed./Header error.',
              '20':'Time value not allowed.',
              }

    #-----------------------
    # init functions
    #-----------------------

    def update(self):
        return self.__init__()

    def __init__(self,network=None,address=None,power=None):

        # init values
        if network != None:
            self.at_id = int(network)
        if address != None:
            self.at_ad = int(address)
        if power != None:
            self.at_rf = int(power)

        # device hart reset
        self.hard_reset()

        # make port
        self.port = UART(1,
                         baudrate=115200,
                         bits=8,
                         parity=None,
                         stop=1,
                         timeout=128,
                         tx=self.uart_tx,
                         rx=self.uart_rx,
                         rxbuf=self.uart_rx_buf,
                         txbuf=self.uart_tx_buf)

        # flush port to start
        self.flush()

        # test port and device
        assert self.isok()

        # set up device
        self.device_setup()

    #-----------------------
    # uart functions
    #-----------------------

    # clear all buffers
    def flush(self,show=True):
        flush = len(self.port.read(self.port.any()))
        flush += len(self.buffer)
        self.buffer = b''
        if show:
            print('FLUSH:',flush)
        return flush

    # move all data from the port buffer to the local buffer
    def buffer_load(self):
        self.buffer += self.port.read(self.port.any())

    # get one line from the local buffer (or '')
    def buffer_line(self):
        line = ''
        if b'\r' in self.buffer:
            line,self.buffer = self.buffer.split(b'\r',1)
            line = line.decode('utf-8','?').strip()
            if line[:5] == '+ERR=':
                code = line.split('=')[-1]
                line += ','+self.errors.get(code,'Unknown error code.')
        return line

    # make sure the local buffer is under 512 bytes
    def buffer_trim(self):
        if self.buffer and len(self.buffer) > 512:
            while len(self.buffer) > 512:
                llen = len(self.buffer_line())
                if not llen:
                    break
                print('BUFFER DUMP:',llen)

    # load buffer and get a single line
    def readline(self,trim=True):
        self.buffer_load()
        line = self.buffer_line()
        if trim:
            self.buffer_trim()
        return line

    # load buffer and iterate through all lines
    def readlines(self,trim=True):
        self.buffer_load()
        while 1:
            line = self.buffer_line()
            if line:
                yield line
            else:
                break
        if trim:
            self.buffer_trim()

    # parse a +RCV line into message components
    def rcvparse(self,line):
        line = line.split('=')[-1]+',,,,'
        a,l,d,r,s = line.split(',')[:5]
        return {'addr':a,'dlen':l,'data':d,'rssi':r,'snr':s}

    # send a line of data to uart
    def sendline(self,line):
        line = line.strip()
        return self.port.write(bytearray(line)+b'\r\n')

    # build and send a AT LORA message
    def send(self,address,message,wait=True):
        message = str(message).strip()[:240]
        self.sendline('AT+SEND={},{},{}'.format(address,len(message),message))
        if wait:
            return self.waitforit() is not None
        return True

    # get [address,length,message] strings from last sent message
    def sent(self):
        self.sendline('AT+SEND?')
        line = self.waitforit('+SEND=')
        if not line:
            return '0','0',''
        return (line[6:]+',,').split(',')[:3]

    # wait for a line that starts with "startswith" until "timeout"
    def waitforit(self,startswith='+OK',timeout=10,show=False):
        now = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(),now) < timeout*1000:
            line = self.readline()
            if not line:
                time.sleep_ms(10)
                continue
            elif line.startswith(startswith):
                if show:
                    print('OKAY:',[line])
                return line
            elif show:
                print('WAIT:',[line])
        if show:
            print('FAIL')
        return None

    #-----------------------
    # device functions
    #-----------------------

    # hard reset of device using reset pin
    def hard_reset(self):

        # reset active == LOW
        Pin(self.reset_pin,Pin.OUT,value=0) 
        time.sleep_ms(100)

        # reset inactive == HIGH
        Pin(self.reset_pin,Pin.OUT,value=1)
        time.sleep_ms(100)

        # reset has an internal pull up
        Pin(self.reset_pin,Pin.IN)

        return True

    # soft reset of device using reset command
    def soft_reset(self):
        self.flush(show=False)
        self.sendline('AT+RESET')
        return self.waitforit('+READY',1,True) is not None

    # ping device with AT and wait for response
    def isok(self):
        self.flush(show=False)
        self.sendline('AT')
        return self.waitforit('+OK',1,True) is not None

    # set device to sleep mode
    def sleep(self):
        self.sendline('AT+MODE=1')
        return self.waitforit('+OK',1,True) is not None

    # send a command to wake device
    def wake(self):
        self.sendline('AT+MODE=0')
        return True

    # set up all device values
    def device_setup(self):

        print('CONFIG:')

        # sender
        def linecheck(line,check='+OK'):
            self.sendline(line)
            success = self.waitforit(check,1,False)
            print('   ',line,success)
            assert success

        # clear to start
        self.flush(show=False)

        # mode 0 = transceiver mode
        # 'AT+MODE=0'
        linecheck('AT+MODE=0')

        # baud = 115200
        # 'AT+IPR=115200'
        linecheck('AT+IPR=115200','+IPR=')

        # parameters = <Spreading Factor>,<Bandwidth>,<Coding Rate>,<Programmed Preamble>
        # parameter defaults = 9,7,1,12
        # 'AT+PARAMETER=7,9,4,12'
        linecheck('AT+PARAMETER={},{},{},{}'.format(self.at_sp,self.at_bw,self.at_cr,self.at_pp))

        # band 915000000 in US
        # 'AT+BAND=915000000'
        linecheck('AT+BAND={}'.format(self.at_bd))

        # address of device 16bit
        # 'AT+ADDRESS=120'
        linecheck('AT+ADDRESS={}'.format(self.at_ad))

        # network id 3-15 or 18=default
        # 'AT+NETWORKID=6'
        linecheck('AT+NETWORKID={}'.format(self.at_id))

        # RF strength 0-22
        # 'AT+CRFOP=10'
        linecheck('AT+CRFOP={}'.format(self.at_rf))

    # get a dict of all device options
    def device_info(self,show=True):

        print('DEVICE:')

        # return value
        info = {}

        # clear to start
        self.flush(show=False)

        # collect/print values
        for item,line,check in [
            ('MODE','AT+MODE?','+MODE'),
            ('IPR','AT+IPR?','+IPR'),
            ('PARAMETER','AT+PARAMETER?','+PARAMETER'),
            ('BAND','AT+BAND?','+BAND'),
            ('ADDRESS','AT+ADDRESS?','+ADDRESS'),
            ('NETWORKID','AT+NETWORKID?','+NETWORKID'),
            ('CRFOP','AT+CRFOP?','+CRFOP'),
            ('UID','AT+UID?','+UID'),
            ('VERSION','AT+VER?','+VER')]:
            self.sendline(line)
            value = self.waitforit(check,1,False).split('=')[-1]
            if item == 'PARAMETER':
                sp,bw,cr,pp = (value+',,,').split(',')[:4]
                info['SP_FACTOR'] = sp
                info['BANDWIDTH'] = bw
                info['CODE_RATE'] = cr
                info['PPREAMBLE'] = pp
                if show:
                    print('    SP_FACTOR: {}'.format(sp))
                    print('    BANDWIDTH: {}'.format(bw))
                    print('    CODE_RATE: {}'.format(cr))
                    print('    PPREAMBLE: {}'.format(pp))
            else:
                info[item] = value
                if show:
                    print('    {}: {}'.format(item,value))

        # done
        return info
        
#-----------------------
# end
#-----------------------
