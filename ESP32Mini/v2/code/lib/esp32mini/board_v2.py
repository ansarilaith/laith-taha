#-----------------------
# imports
#-----------------------

from micropython import const

#-----------------------
# esp32mini variables class
#-----------------------

class BOARD:

    BOARD_NAME = 'ESP32MINI-V2'
    BOARD_DATE = '2021-10-28'

    PIN_MANRST    = const(4) #  --> RESET
    PIN_LED       = const(2) # Blue LED
    PIN_PROG      = const(0) # PROG Button

    helplines = '''

    key 1 esp32mini info, help, and variables
        esp32mini.info # version and name
        esp32mini.help # basic help
        esp32mini.show('module') # more detailed help 
        dir(esp32mini) # lists a bunch of pins

    key 2 esp32 esp32 sensors, values, reset
        esp32.reset # hard reset
        esp32.temp # temperature C
        esp32.tempf # temperature F
        esp32.hall # read hall sensor
        esp32.memory # memory use
        esp32.flash # disk use

    key 4 led control the blue led 
        led.on()
        led.off()
        led.blink(count) # blink "count" times
        led.pwm(percent) # use pwm to dim the led
        led.pwm2(p1,p2) # change led from p1 to p2
        led.pwmx() # turn off pwm

    key 7 wifi connect to local wifi
        set: essid = "my_essid"
        set: password = "my_password"
        wifi.scan() # list available access points
        wifi.connect(essid,password) # or use set values
        wifi.ip() # return current IP
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
        eziot.watch(startrows,update,group,device)
        eziot.post_data(group,device,data1,data2,data3,data4)
        eziot.get_data(count,after,group,device)
        eziot.delete_data(rowids,before,xall)
        eziot.get_dns() # get current DNS setup
        eziot.set_dns(port,dnsid) # set and start DNS
        eziot.unset_dns() # stop DNS service        

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
        st.???() # more functions, see the docs
        
            '''

    ASCIIART = r'''
  _____ _____ _____ _____ _____   __    __ _       _ 
 |  ___|  ___|  _  |___  |___  | |  \  /  |_|     |_|
 | |__ | |___| |_| | __| | __| | |   \/   |_ _ ___ _ 
 |  __||___  |  ___||__  |/ ___| | |\  /| | | '_  | |
 | |___ ___| | |    ___| | |___  | | \/ | | | | | | |
 |_____|_____|_|   |_____|_____| |_|    |_|_|_| |_|_| v2

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
            print('ESP32Mini MODULE: {}'.format(module))
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

#-----------------------
# end
#-----------------------
