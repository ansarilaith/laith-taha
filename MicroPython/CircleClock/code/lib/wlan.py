#-----------------------
# notify
#-----------------------

# Stolen from Clayton Darwin

print('LOAD: wlan.py')

#-----------------------
# notes
#-----------------------

# config file = a csv-type file
# read any line starting with "wlan" or "ap"
# commas and whitespace will cause a break
# a # will end line parsing (ignore after)
# other line types ignored
# example:
# wlan,myessid1,mypassword1 # required
# wlan,myessid2,mypassword2 # optional
# wlan,hostname,myhostname  # optional
# wlan,dns,8.8.8.8          # optional
# wlan,timeout,10           # optional, must be an int
# ap,essid,essid
# ap,password,password
# ap,ip,192.168.4.1

#-----------------------
# imports
#-----------------------

from time import sleep_ms, gmtime
from network import WLAN, STA_IF, AP_IF

#-----------------------
# global variables
#-----------------------

default_confile  = 'config.txt' # config file name, a csv file, in root or /sd
default_essid    = 'clayton'
default_password = 'clayton'
default_hostname = 'clayton'
default_ip       = '10.0.0.1' # micropython default is '192.168.4.1'
default_dns      = '8.8.8.8' # google
default_timeout  = 8

#-----------------------
# common variables + functions
#-----------------------

def add_wlan_creds(confile,essid,password):
    # fix credentials
    if not (essid and password):
        return essid,password,False
    essid = ''.join(essid.split())
    password = ''.join(password.split())
    print('ADD WLAN CREDS:',[essid,password])
    # update files, put new cred first
    success = False
    for file in ('/sd/'+confile,confile):
        # read
        print('  READ:',file,end=' ')
        lines = ['wlan,{},{}'.format(essid,password)]
        try:
            with open(file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if not line.startswith('wlan'):
                            lines.append(line)                       
                        else:
                            line2 = [x.strip() for x in line.split('#',1)[0].replace(',',' ').split() if x.strip()] # smash 3
                            if line2[:2] != ['wlan',essid]:
                                lines.append(line)
                f.close()
            print('OKAY')
        except:
            print('ERROR')
            continue # don't write if you couldn't read
        # write
        for line in lines:
            print('  LINE:',[line])
        print('  WRITE:',file,end=' ')
        try:
            with open(file,'w') as f:
                for line in lines:
                    f.write(line+'\n')
                f.close()
            success = True
            print('OKAY')
        except:
            print('ERROR')
    # done
    return essid,password,success

#-----------------------
# access point class
#-----------------------

class AP:

    #-----------------------
    # variables
    #-----------------------

    essid    = 'clayton'
    password = 'clayton'
    ip       = '10.0.0.1' # micropython default is '192.168.4.1'
    clients  = 10
    authmode = 3
    mac = None
    ap = None

    #-----------------------
    # init
    #-----------------------

    def __init__(self,connect=False,confile=None,essid=None,password=None,ip=None):

        # update values
        self.confile = confile or default_confile
        self.essid = essid or default_essis
        self.password = password or default_password
        self.ip = ip or default_ip

        # clear WLAN
        WLAN(STA_IF).active(False)

        # create ap object
        self.ap = WLAN(AP_IF)
        self.ap.active(False)
        sleep_ms(100)

        # load mac
        from ubinascii import hexlify
        mac = hexlify(self.ap.config('mac')).decode('ascii')
        del hexlify
        mac = list(mac)
        for x in range(10,0,-2):
            mac.insert(x,':')
        self.mac = ''.join(mac)

        # connect
        if connect:
            self.connect()

    #-----------------------
    # connect
    #-----------------------

    def connect(self):

        # already running
        if self.ap.active():
            print('WLAN AP ACTIVE')
            return None

        # setup
        print('WLAN AP SETUP:')
        WLAN(STA_IF).active(False)

        # get current creds
        self.read_confile()

        # activate
        self.ap.active(True)
        sleep_ms(100)
        while not self.ap.active():
            sleep_ms(100)

        # deactivate
        self.ap.active(False)

        # build
        # subnet=standard, gateway = ip, dns=google (won't work)
        self.ap.ifconfig((self.ip,'255.255.255.0',self.ip,'8.8.8.8'))
        self.ap.config(max_clients=self.clients)
        self.ap.config(essid=self.essid)
        self.ap.config(password=self.password)
        self.ap.config(authmode=self.authmode)

        # reactivate
        self.ap.active(True)
        while not self.ap.active():
            time.sleep_ms(10)

        # show
        ip,subnet,gateway,dns = self.ap.ifconfig()
        print('  IP:',ip)
        print('  ESSID:',self.ap.config('essid'))
        print('  PASSWORD:',self.password)
        print('  SUBNET:',subnet)
        print('  GATEWAY:',gateway)
        print('  DNS:',dns)
        print('  MAC:',self.mac)
        print('  CHANNEL:',self.ap.config('channel'))
        print('  AUTHMODE:',self.ap.config('authmode'))

        # done
        return True

    def isconnected(self):
        return self.ap.active()

    #-----------------------
    # disconnect
    #-----------------------

    def disconnect(self):
        print('WLAN AP X:',end=' ')
        try:
            self.ap.active(False)
        except:
            self.ap = None
        return True

    #-----------------------
    # sub functions
    #-----------------------

    def add_wlan_creds(self,essid,password):
        return add_wlan_creds(self.confile,essid,password)[-1]

    def read_confile(self):
        for file in ('/sd/'+self.confile,self.confile):
            print('WLAN AP CREDS:',file,end=' ')
            try:
                with open(file) as f:
                    print(True) # file opened
                    for line in f:
                        if line.startswith('ap'):
                            line = [x.strip() for x in line.split('#',1)[0].replace(',',' ').split() if x.strip()] # smash 3
                            if line[0] == 'ap' and len(line) >= 3:
                                if line[1] == 'essid':
                                    self.essid = line[2]
                                    print('  essid:',self.essid)
                                elif line[1] == 'password':
                                    self.password = line[2] or None
                                    print('  password:',self.password)
                                elif line[1] == 'ip':
                                    self.ip = line[2]
                                    print('  ip:',self.ip)
                    f.close()
                return True
            except Exception as e:
                print(False)
        return False
        
    def set_rtc(self,tries=10,only_if_needed=True):
        # not connected to network
        return False

#-----------------------
# station class
#-----------------------

class STA:

    #-----------------------
    # variables
    #-----------------------

    # credentials
    creds = []

    # hostname
    hostname = 'clayton'

    # dns
    dns = '8.8.8.8'

    # connect/disconnect timeout seconds
    timeout = 8

    # connection objects
    wlan = None
    mac = None
    essid = None
    ip = None

    #-----------------------
    # init
    #-----------------------

    def __init__(self,connect=False,confile=None,creds=[],hostname=None,dns=None,timeout=None):

        # update values
        self.confile = confile or default_confile
        self.dns = dns or default_dns
        self.timeout = timeout or default_timeout
        self.hostname = hostname or default_hostname
        if creds:
            self.creds = creds

        # clear WLAN
        WLAN(AP_IF).active(False)
        sleep_ms(100)

        # create wlan object
        self.wlan = WLAN(STA_IF)
        self.wlan.active(False)
        sleep_ms(100)

        # load mac
        from ubinascii import hexlify
        mac = hexlify(self.wlan.config('mac')).decode('ascii')
        del hexlify
        mac = list(mac)
        for x in range(10,0,-2):
            mac.insert(x,':')
        self.mac = ''.join(mac)

        # connect
        if connect:
            self.connect()

    #-----------------------
    # connect (re-connect)
    #-----------------------

    def connect(self,essid=None,password=None,confile=None):

        # already connected
        if self.wlan.active() and self.wlan.isconnected:
            print('WLAN STA CONNECTED')
            return None

        # connect
        print('WLAN STA CONNECT:')
        WLAN(AP_IF).active(False)

        # get current creds
        self.read_confile()

        # clear variables
        self.essid,self.ip = None,None

        # activate
        self.wlan.active(True)
        sleep_ms(100)
        while not self.wlan.active():
            sleep_ms(10)

        # set hostname
        self.wlan.config(hostname=self.hostname)

        # get available networks
        essids = self.read_essids()
        print('ESSIDS:',essids)

        # connect to first available
        status = False
        for e,p in [(essid,password)]+self.creds:
            if e:
                print('  ESSID:',[e,p],end=' ')
                if e not in essids:
                    print('NOT AVAILABLE')
                    continue
                self.wlan.connect(e,p)
                for x in range(self.timeout*10):
                    status = self.wlan.isconnected()
                    if status:
                        break
                    sleep_ms(100)
                if status:
                    self.essid = e
                    print(True)
                    break
                else:
                    print(False,end=' ')
                    self.wlan.disconnect()
                    for x in range(self.timeout*10):
                        if not self.wlan.isconnected():
                            print('WLANX',end=' ')
                            break
                        sleep_ms(100)
                    print('')
            if status:
                break

        # update connect data
        print('WLAN STA STATUS:',status)
        if status:
            ipdata = list(self.wlan.ifconfig())
            self.ip = ipdata[0]
            # set dns
            if ipdata[-1] != self.dns:
                ipdata[-1] = self.dns
                self.wlan.ifconfig(ipdata)
                ipdata = list(self.wlan.ifconfig())
        print('WLAN STA: {} {} {}'.format(self.mac,self.ip,self.essid))

        # done
        return status

    def isconnected(self):
        return self.wlan.isconnected()

    #-----------------------
    # disconnect
    #-----------------------

    def disconnect(self):
        print('WLAN STA X:',end=' ')
        status = True
        if self.wlan.active():
            if self.wlan.isconnected():
                self.wlan.disconnect()
                for x in range(self.timeout*10):
                    if not self.wlan.isconnected():
                        break
                    sleep_ms(100)
                status = not self.wlan.isconnected()
        print(status)
        self.wlan.active(False)
        self.essid,self.ip = None,None
        return status

    #-----------------------
    # sub functions
    #-----------------------

    def add_wlan_creds(self,essid,password):
        essid,password,success = add_wlan_creds(self.confile,essid,password)
        if success:
            self.creds = [(essid,password)] + [x for x in self.creds if x[0] != essid]
        return success

    def read_confile(self):
        creds = []
        for file in ('/sd/'+self.confile,self.confile):
            print('WLAN STA CREDS:',file,end=' ')
            try:
                with open(file) as f:
                    print(True) # file opened
                    for line in f:
                        if line.startswith('wlan'):
                            line = [x.strip() for x in line.split('#',1)[0].replace(',',' ').split() if x.strip()] # smash 3
                            if line[0] == 'wlan' and len(line) >= 3:
                                if line[1] == 'hostname':
                                    self.hostname = line[2]
                                    print('  hostname:',self.hostname)
                                elif line[1] == 'dns':
                                    self.dns = line[2]
                                    print('  dns:',self.dns)
                                elif line[1] == 'timeout' and line[2].isdigit():
                                    self.timeout = int(line[2])
                                    print('  timeout:',self.timeout)
                                else:
                                    creds.append((line[1],line[2]))
                                    print('  creds:',line[1:3])
                    f.close()
                    self.creds = creds
                return True
            except Exception as e:
                print(False)
        return False

    def read_essids(self):
        state = self.wlan.active() # save for later
        if not state:
            self.wlan.active(True)
        essids = [x[0].decode('latin1') for x in self.wlan.scan()]
        if not state: # restore to original
            self.wlan.active(False)
        return essids
        
    def set_rtc(self,tries=10,only_if_needed=True):
        if only_if_needed and gmtime()[0] >= 2022:
            return True
        from ntptime import settime
        for x in range(tries):
            try:
                settime()
                print('RTC NTP OK')
                del settime
                return True
            except:
                print('RTC NTP XX')
        print('RTC NTP FAILED!')
        del settime
        return False

##    def network_list(self,show_only=True):
##        # imports        
##        from ubinascii import hexlify
##        # set wlan active (save current state)
##        state = self.wlan.active()
##        if not state:
##            self.wlan.active(True)
##        # collect networks
##        nets = []
##        for ssid,bssid,channel,RSSI,authmode,hidden in self.wlan.scan():
##            ssid = ssid.decode('ascii')
##            bssid = hexlify(bssid).decode('ascii')
##            if len(bssid) == 12:
##                bssid = ':'.join([bssid[x:x+2] for x in range(0,12,2)])
##            authmode = ('OPEN','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK')[min(4,max(0,authmode))]
##            if hidden:
##                hidden = True
##            else:
##                hidden = False
##                nets.append((ssid,bssid,channel,RSSI,authmode,hidden))
##        # return to pervious state
##        if not state:
##            self.wlan.active(False)
##        # del imports
##        del hexlify
##        # done
##        if show_only:
##            for x in nets:
##                print('NET AP:',x)
##        else:
##            return nets

##    def status(self):
##        return {200 :'STAT_BEACON_TIMEOUT',
##                201 :'STAT_NO_AP_FOUND',
##                202 :'STAT_WRONG_PASSWORD',
##                203 :'STAT_ASSOC_FAIL',
##                204 :'STAT_HANDSHAKE_TIMEOUT',
##                1000:'STAT_IDLE',
##                1001:'STAT_CONNECTING',
##                1010:'STAT_GOT_IP',
##                }.get(self.wlan.status(),'STAT_UNKNOWN')

#-----------------------
# end
#-----------------------

