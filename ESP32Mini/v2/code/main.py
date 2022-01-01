# main.py
import time
import sys

# connect to wifi
print('\nWIFI SCAN')
wifi.scan()
wifi.essid = 'youressid'
wifi.password = 'yourpassword'
print('\nWIFI CONNECT')
wifi.connect()

# set your clock (may take several tries)
print('\nSET Real-Time Clock')
for x in range(10):
    if rtc.ntp_set():
        break
    time.sleep_ms(500)

# watch/check eziot
print('\nCHECK EZIOT')
eziot.api_key = 'EXAMPLE'
eziot.api_secret = 'EXAMPLE'
#eziot.watch()
for x in eziot.get_data(5):
    print('EZIOT DATUM:',x[2:])
print()

# run LED fade-in fade-out
print('\nCHECK LED')
try:
    #while 1:
    for x in range(3):
        led.pwm2(0,100,10)
        print('LED ON')
        led.pwm2(100,0,10)
        print('LED OFF')
        time.sleep_ms(100)
except KeyboardInterrupt:
    pass
except Exception as e:
    print('LED ERROR:',sys.print_exception(e))
    pass
led.off()

# test a few other built-in functions
print('\nTEST BUILT-INS')

print('\nst.tree:')
st.tree()

print('\nst.memp:')
st.memp()

print('\nesp32mini:')
print('INFO:',esp32mini.help)
esp32mini.help
print('SHOW st:')
esp32mini.show('st')

print('\nesp32:')
print('TEMP C:',esp32.temp)
print('TEMP F:',esp32.tempf)
print('HALL SENSOR:',esp32.hall)
print('MEM STATS:',esp32.memory)
print('FLASH STATS:',esp32.flash)

# done
print('\nAll tests complete.')

# infinite loop: flash LED
c = 0
while 1:
    c += 1
    print('loop',c)
    led.on()
    time.sleep_ms(100)
    led.off()
    time.sleep_ms(900)

    
    

