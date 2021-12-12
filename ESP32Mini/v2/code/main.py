# main.py

# connect to wifi
wifi.scan()
wifi.essid = 'youressid'
wifi.password = 'yourpassword'
wifi.connect()

# set your clock (may take several tries)
import time
for x in range(10):
    if rtc.ntp_set():
        break
    time.sleep_ms(500)

# watch eziot 
#eziot.api_key = 'EXAMPLE'
#eziot.api_secret = 'EXAMPLE'
#eziot.watch()

# run LED
import time,sys
try:
    while 1:
        led.pwm2(0,100,10)
        led.pwm2(100,0,10)
        time.sleep_ms(1000)
except Exception as e:
    print('LED ERROR:',sys.print_exception(e))
    pass
led.off()
    
    

