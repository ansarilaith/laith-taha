#-----------------------
# imports
#-----------------------

from micropython import const

#-----------------------
# funboard variables class
#-----------------------

class BOARD:

    BOARD_NAME = 'FUNBOARD-V2'
    BOARD_DATE = '2021-04-07'

    # sdcard ref: https://docs.micropython.org/en/latest/library/machine.SDCard.html
    SDCARD_SLOT   = const( 3) #
    PIN_SD_CS     = const(15) # SDCard Slot 3
    PIN_SD_SCL    = const(14) # SDCard Slot 3
    PIN_SD_MOSI   = const(13) # SDCard Slot 3
    PIN_SD_MISO   = const(12) # SDCard Slot 3
    
    PIN_MANRST    = const(27) #  --> RESET
    PIN_LED       = const(32) # Blue LED
    PIN_PIXELS    = const( 4) # 8 Micro Pixels
    PIN_BUZZER    = const( 2) # Buzzer
    PIN_PROG      = const( 0) # PROG Button
    PIN_UART1_TX  = const(17) # UART
    PIN_UART1_RX  = const(16) # UART
    PIN_SPI2_CS   = const( 5) # SPI-2
    PIN_SPI2_SCL  = const(18) # SPI-2
    PIN_SPI2_MISO = const(19) # SPI-2
    PIN_SPI2_MOSI = const(23) # SPI-2
    PIN_I2C1_DATA = const(26) # I2C-1
    PIN_I2C1_CLK  = const(25) # I2C-1

    helplines = '''

    key 1 funboard info, help, and variables
        funboard.info # version and name
        funboard.help # basic help
        funboard.show('module') # more detailed help 
        dir(funboard) # lists a bunch of pins

    key 2 esp32 esp32 sensors, values, reset
        esp32.reset # hard reset
        esp32.temp # temperature C
        esp32.tempf # temperature F
        esp32.hall # read hall sensor
        esp32.memory # memory use
        esp32.flash # disk use

    key 3 beeper beep the buzzer
        beeper.beep() # beep
        beeper.beepn(count) # beep n times
        beeper.beep2(freq1,freq2) # a beep that changes freq
        beeper.play(notestring) # play a string of notes

    key 4 led control the blue led 
        led.on()
        led.off()
        led.blink(count) # blink "count" times
        led.pwm(percent) # use pwm to dim the led
        led.pwm2(p1,p2) # change led from p1 to p2 

    key 5 pixels control the funboard micro pixels
        set: pixels.brightness = 32 # 0-255, set global
        pixels.off() # all off
        pixels.kill() # makes gpio pin an imput
        pixels.setp(pixel,color,brightness) # set a pixel 0-7
        pixels.set_brightness(32) # set global, adjust current
        pixels.sweep(color,brightness) # like KITT from Knight Rider

    key 6 sdcard SDcard mount, format, etc
        sdcard.mount() # mount sd card, runs on boot
        sdcard.unmount() # unmount sdcard to remove it
        sdcard.sdpath() # show path to sd card
        sdcard.format() # erase/format the sd card

    key 7 wifi connect to local wifi
        set: essid = "my_essid"
        set: password = "my_password"
        wifi.scan() # list available access points
        wifi.connect(essid,password) # or use set values
        wifi.disconnect()

    key 8 rtc real time clock functions
        rtc.ntp_set() # set time (after wifi connect)
        rtc.set(datetime_tuple) # manual set
        rtc.get() # get the rtc time
        rtc.linux_epoch() # seconds since jan 1 1970
        rtc.dtstamp() # datetime string

    key 9 eziot store data on the cloud
        set: eziot.api_key = "my_account_key"
        set: eziot.api_secret = "my_account_secret"
        set: eziot.api_version = 1.0
        eziot.stats()
        eziot.post_data(group,device,data1,data2,data3,data4)
        eziot.get_data(count,after,group,device)
        eziot.delete_data(rowids,before,xall)
        eziot.watch(startrows,update,group,device)

    key 10 st system tools for dirs, file, etc.
        st.tree() # print directory tree structure
        st.remove('filepath') # remove a file
        st.rmdir('dirpath') # remove a dir
        st.isfile('path')
        st.isdir('path')
        st.exists('path')
        st.abspath('path')
        st.mkdir('dirpath')
        st.pf('filepath') # print file to screen
        st.pp(object) # pretty print a dict, list, etc
        st.reload(module) # reload module
        st.du() # show disk usage
        st.memp() # clean memory and show usage percent
        st. ... # more functions, see the docs
        
            '''

    ASCIIART = r'''
  _____            _____                      _     _______
 |  ___|          |  _  |                    | |   / _   _ \
 | |__ _   _ _ ___| |_| |_____  __ _ ____ ___| |  / (.) (.) \
 |  __| | | | '_  |  _ <|  _  |/ _' |  __|  _  | (  _     _  )
 | |  | |_| | | | | |_| | |_| | |_| | |  | |_| |  \  \___/  /
 |_|  |_____|_| |_|_____|_____|___,_|_|  |_____|   \_______/

          From ClaytonDarwin on YouTube
    '''

    def __init__(self):

        # build help
        self.help1,self.help2 = [],{}
        self.helplines = self.helplines.split('\n')
        key = ''
        for line in self.helplines:
            line = line.strip()
            if line:
                if line.startswith('key '):
                    nada,order,key,desc = ([x.strip() for x in line.split(None,3)]+['','','',''])[:4]
                    if order.isdigit():
                        order = int(order)
                    else:
                        order = 1000
                    self.help1.append((order,key,desc))
                    self.help2[key] = [] 
                else:
                    self.help2[key].append(line)
        del self.helplines
        self.help1.sort()
        self.help1 = [(key,desc) for order,key,desc in self.help1]

    @property
    def info(self):
        print('{} {}'.format(self.BOARD_NAME,self.BOARD_DATE))

    @property
    def help(self):
        print('{} Extras:'.format(self.BOARD_NAME))
        width = max([len(key) for key,desc in self.help1])
        for key,desc in self.help1:
            key = key + ' '*max(0,width-len(key))
            if desc:
                print('    {} = {}'.format(key,desc))
            else:
                print('    {}'.format(key))

    def show(self,module=None):
        if module not in self.help2:
            print('Unknown MODULE: {}'.format(module))
        else:
            print('FunBoard MODULE: {}'.format(module))
            width = max([len(x.split('#')[0].strip()) for x in self.help2[module]])
            for line in self.help2[module]:
                funct,desc = [x.strip() for x in (line+'#').split('#')][:2]
                funct = funct + ' '*max(0,width-len(funct))
                if desc:
                    print('    {} = {}'.format(funct,desc))
                else:
                    print('    {}'.format(funct))
            print('Be sure to check the documentation for details!')
            print('GitLab: https://gitlab.com/duder1966/youtube-projects')

    def test(self):
        led.on()
        beeper.beep()
        pixels.sweep('red',ontime=100,offtime=100)
        st.tree()
        pixels.sweep('blue',ontime=100,offtime=100)
        wifi.scan()
        pixels.sweep('green',ontime=100,offtime=100)
        led.off()
        esp32.reset()

#-----------------------
# end
#-----------------------
