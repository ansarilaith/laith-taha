

# connect to wifi
wifi.essid = 'DARWIN-NET-TEST'
wifi.password = 'claytondarwin'
wifi.scan()
wifi.connect()

# set your clock (may take several tries)
import time
for x in range(3):
    if rtc.ntp_set():
        break
    time.sleep_ms(500)

# watch eziot 
eziot.api_key = 'EXAMPLE'
eziot.api_secret = 'EXAMPLE'
eziot.watch()


