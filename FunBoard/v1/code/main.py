
# connect to wifi
wifi.essid = 'DARWIN-NET-TEST'
wifi.password = 'claytondarwin'
wifi.scan()
wifi.connect()

# set your clock (may take several tries)
for x in range(3):
    if rtc.ntp_set():
        break
    rtc.time.sleep_ms(500)

# watch eziot 
eziot.api_key = 'EXAMPLE'
eziot.api_secret = 'EXAMPLE'
eziot.watch()


