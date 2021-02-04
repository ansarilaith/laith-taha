# Posty Project: main.py
# Copyright (c) 2019 Clayton Darwin claytondarwin@gmail.com

# notify
print('RUN: main.py')

# imports

import os
import sys
import time
import gpio_beep
import gpio_leds
from nettools import wlan_connect,wlan_disconnect
import opensocket_server

# beeper + light

beeper  = gpio_beep.BEEP(2)
blinker = gpio_leds.LED(32)

def beep(n=1):
    for x in range(n):
        blinker.on()
        beeper.beep()
        blinker.off()
        time.sleep_ms(100)

# socket server application
def application(line):
    print('  APP LINEIN:',line)
    beep()
    if not line:
        return 'ERROR no data'
    elif line == b'PING':
        print('    RETURN:',b'PING Example APP')
        return b'PING Example APP'
    elif line == b'EOD':
        return line
    elif line[:8] == b'_client:':
        return line
    elif line[:4] == b'_ip:':
        return line
    else:
        print('    RETURN:',b'BOUNCE '+line)
        return b'BOUNCE '+line

# server loop
while 1:

    print('OpenSocket Server Starting')
    beep(2)

    # network connect
    # these are placeholders, use your own
    essid = 'DARWIN-NET-X'
    essid_password = 'claytondarwinsecretpassword' 
    wlan_connect(essid,essid_password,timeout=15)

    # server setup
    server = opensocket_server.OpenSocket_Server()
    server.server_host = '0.0.0.0'
    server.server_port = 8888
    server.client_timeout = 10
    server.application = application    

    # server start
    try:
        server.serve()
    except KeyboardInterrupt:
        break
    except Exception as e:
        sys.print_exception(e)

    # network disconnect
    wlan_disconnect()

    # end
    print('OpenSocket Server Ended')








