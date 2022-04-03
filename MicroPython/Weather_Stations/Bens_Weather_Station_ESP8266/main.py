# notify
print('RUN: main.py')

# this is the ESP8266 D1 Mini pinout
#                           -------
#      WAKE <--        RST |     TX| G01 - TXD0
#                      AD0 |A0   RX| G03 - RXD0
#       RST <-- WAKE - G16 |D0   D1| G05 - SCL   --> SCL BME280
#               SCLK - G14 |D5   D2| G04 - SDA   --> SDA BME280
# GREEN LED <-- MISO - G12 |D6   D3| G00 - FLASH --> GND BME280
#   RED LED <-- MOSI - G13 |D7   D4| G02 -       --> built-in BLUE LED
#               CS   - G15 |D8     | GND -
# BME280VSS <--      - 3.3 |       | 5.0 -
# LEDs ANODE                -------
#                             USB

# immediate pin set
from machine import Pin
Pin( 2,Pin.IN)
Pin(12,Pin.IN)
Pin(13,Pin.IN)
Pin( 0,Pin.IN)
Pin( 4,Pin.IN)
Pin( 5,Pin.IN)
red = 13
grn = 12
blu =  2
scl =  5
sda =  4
gnd =  0

# universal imports
import time,gc
gc.collect()

# blink an LED on pin
def blink(pin,ms=125):
    p = Pin(pin,Pin.OUT)
    p.value(0)
    time.sleep_ms(ms)
    p.value(1)
    Pin(pin,Pin.IN)

# BME280 function
def get_bme280_data():

    print('READ BME280:')

    # imports
    from machine import I2C
    import bme280
    gc.collect()

    # catch
    try:
    
        # bme280 ground is GPIO2
        # see I2C pins/specs below

        # elevation in meters
        elevation = 730 * 0.3048 # convert feet to meters

        # turn on device
        ground = Pin(gnd,Pin.OUT)
        ground.value(0)
        time.sleep_ms(250)

        # set I2C
        freq = 100000 # low rate to start (try x4 for max)
        iic = I2C(scl=Pin(scl),sda=Pin(sda),freq=freq)

        # set up bme280
        BME280 = bme280.BME280(mode=bme280.BME280_OSAMPLE_16,i2c=iic)

        # sample
        for x in range(3):
            BME280.read_compensated_data()
            #time.sleep_ms(500)
        time.sleep_ms(250)
        t1,p1,h1 = BME280.read_compensated_data()

        # convert temp to F
        t2 = t1/100 # C (save for pressure)
        T = t2 * 1.8 + 32

        # convert humidity to %
        H = h1/1024

        # convert pressure to inches Hg
        # pressure is reported adjusted to sea level
        P = (p1/256) # pascals
        P *= ( 1 - ( (0.0065*elevation) / (t2 + 0.0065*elevation + 273.15) ) )**-5.257 # sea level adjust formula
        P /= 3386.3887 # inches of Hg

        # references
        # 1 inch of mercury == 3386.3886666667 pascal
        # 1 pascal == 0.27305296782499 foot of air [15 °C]
        # 3.66229310 pascals per foot
        # sea level is 101325 pascals at standard temp
        # Home is 730 feet = 101325 - (3.66229310*730) = 98651.526037 (minus because going up is less pressure)
        # feet per meter 3.28084

        # turn off device
        ground.value(1)
        ground = Pin(gnd,Pin.IN)

        # good
        blink(grn)

    # catch
    except KeyboardInterrupt:
        raise KeyboardInterrupt

    # catch
    except:
        print('SEND ERROR')
        T,H,P = 0,0,0
        blink(red)
        time.sleep_ms(250)
        blink(red)
        

    # show
    print('TEMP: {:.2f}F'.format(T))
    print('HUMI: {:.2f}%'.format(H))
    print('PRES: {:.2f}Hg'.format(P))

    # done
    return T,H,P

# send function
def send_data(T,H,P):

    print('SEND DATA')
    
    # imports
    from netcreds import essid,essid_password
    from nettools import wlan_connect,wlan_disconnect
    import urequests
    gc.collect()

    # catch
    try:

        # connect
        wlan_connect(essid,essid_password,timeout=30)

        # make request
        jdata = {'T':T,
                 'H':H,
                 'P':P,
                 'U':'793coilerd'} # device location ID
        response = urequests.post('http://symple.design/ben/cgi-bin/weathertrack.py',json=jdata)
        code = response.content
        response.close() # important

        # disconnect
        wlan_disconnect(timeout=15)

        # check
        if b'OK' in code:
            blink(grn)
        else:
            print('SERVER ERROR')
            blink(red)

    # catch
    except KeyboardInterrupt:
        raise KeyboardInterrupt

    # catch
    except:
        print('SEND ERROR')
        blink(red)
        time.sleep_ms(250)
        blink(red)

# deep sleep function
def deep_sleep_mins(mins=1):

    # pause for interrupt
    #print('DEEP SLEEP in 1 sec.')
    #time.sleep_ms(1000)

    print('DEEP SLEEP MINS:',mins)
    
    # ESP8266 connect reset pin to GPIO16
    # GPIO 16 (also D0) is the alarm pin of RTC

    # imports
    import machine

    # get msecs
    msecs = int(mins*60*1000)

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0,wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after msecs (wakes the device)
    rtc.alarm(rtc.ALARM0,msecs)
    

    #put the device to sleep
    machine.deepsleep()

# run sequence
blink(red)
values = get_bme280_data()
if values != (0,0,0):
    send_data(*values)
deep_sleep_mins(10)

