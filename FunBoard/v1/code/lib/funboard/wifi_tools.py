#-----------------------
# imports
#-----------------------

import time
import network
from ubinascii import hexlify

#-----------------------
# notes
#-----------------------

#-----------------------
# wifi class
#-----------------------

class WIFI:

    #-----------------------
    # variables
    #-----------------------

    essid = None
    password = None

    #-----------------------
    # functions
    #-----------------------

    def scan(self):
        wlan = network.WLAN(network.STA_IF)
        state = wlan.active() # save current state
        wlan.active(True) # set state active
        for ssid,bssid,channel,RSSI,authmode,hidden in wlan.scan():
            ssid = ssid.decode('ascii')
            bssid = hexlify(bssid).decode('ascii')
            if len(bssid) == 12:
                bssid = ':'.join([bssid[x:x+2] for x in range(0,12,2)])
            authmode = ('OPEN','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK')[min(4,max(0,authmode))]
            if hidden:
                hidden = True
            else:
                False
            print('Network AP:',[ssid,bssid,channel,RSSI,authmode,hidden])
        wlan.active(state) # return to pervious state

    def connect(self,essid=None,password=None,timeout=15):
        essid = essid or self.essid
        password = password or self.password
        print('Network Connect:',essid)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(essid,password)
            time.sleep_ms(100)
            for x in range(timeout):
                if wlan.isconnected():
                    break
                time.sleep_ms(500)
        return_value = wlan.isconnected()
        print('Network Connect:',essid,return_value)
        return return_value

    def disconnect(self,timeout=15):
        print('Network Disconnect')
        wlan = network.WLAN(network.STA_IF)
        return_value = True
        if wlan.active():
            if wlan.isconnected():
                wlan.disconnect()
                time.sleep_ms(100)
                for x in range(timeout):
                    if not wlan.isconnected():
                        break
                    time.sleep_ms(1000)
                return_value = not wlan.isconnected()
        wlan.active(False)
        print('Network Disonnect:',return_value)
        return return_value

#-----------------------
# end
#-----------------------


