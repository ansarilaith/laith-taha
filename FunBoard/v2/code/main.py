# install version of main.py
# this does some tests then re-writes itself

def isokay(prompt):
    if (input(prompt+' ').strip().lower()+'y')[0] == 'y':
        return True
    return False

# check leds
while 1:
    led.off()
    input('Ready to check LED.')
    led.on()
    if isokay('Green and blue LEDs are on?'):
        break
led.off()

# check pixels
while 1:
    input('Ready to check pixels.')
    pixels.sweep('white',None,200,10)
    if isokay('Pixels okay?'):
        break
pixels.off()

# check beeper
while 1:
    beeper.beep()
    if isokay('Did you hear a beep?'):
        break

# check sd card
while 1:
    print('SDcard mount:',sdcard.mount())
    st.tree('/sd')
    if isokay('Did the SDcard mount?'):
        break

# check wifi
while 1:
    wifi.essid = 'youressid'
    wifi.password = 'yourpassword'
    wifi.scan()
    wifi.connect()
    import time
    for x in range(10):
        if rtc.ntp_set():
            break
        time.sleep_ms(500)
    eziot.api_key = 'EXAMPLE'
    eziot.api_secret = 'EXAMPLE'
    for row in eziot.get_data(10):
        print('    EZIOT:',row)
    if isokay('Is the WiFi okay?'):
        break

# redo main.py
text = """# example main.py

### connect to wifi
##wifi.essid = 'youressid'
##wifi.password = 'yourpassword'
##wifi.scan()
##wifi.connect()

### set your clock (may take several tries)
##import time
##for x in range(3):
##    if rtc.ntp_set():
##        break
##    time.sleep_ms(500)

### watch eziot 
##eziot.api_key = 'EXAMPLE'
##eziot.api_secret = 'EXAMPLE'
##eziot.watch()

"""
if (input('Re-Write main.py?').strip().lower()+'y')[0] == 'y':
    f = open('main.py','w')
    f.write(text)
    f.close()

# done
print('MAIN TEST COMPLETE')


