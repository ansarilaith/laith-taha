#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: main.py')

#-----------------------
# variables
#-----------------------

wifi_essid = 'youressid'
wifi_password = 'yourpassword'

eziot_api_key = 'EXAMPLE' 
eziot_api_secret = 'EXAMPLE'
eziot_group = 'WEATHER'
eziot_device = "CLAYTON2"

i2c_scl = 25 # pin number
i2c_sda = 26 # pin number
i2c_frq = 400000 # frequency

bme_neg = 13 # negative pin on bme280
bme_pos = 14 # positive pin on bme280
bme_address = 118 # default i2c address for bme280
bme_local_altitude = 222 # meters above sea level
bme_weather_us = True

#-----------------------
# imports
#-----------------------

import sys
import time
from machine import Pin

import bus_i2c
import sensor_bme280
import eziot_micropython_minimal as eziot

#-----------------------
# main loop
#-----------------------

def run():

    # setup loop (loop forever)
    while 1:

        # catch
        try:

            # set up wifi
            eziot.wifi_scan()
            eziot.wifi_connect(wifi_essid,wifi_password)

            # set up eziot
            eziot.api_key = eziot_api_key
            eziot.api_secret = eziot_api_secret

            # cycle bme power
            Pin(bme_pos,Pin.IN)
            Pin(bme_neg,Pin.IN)
            time.sleep_ms(200)
            Pin(bme_neg,Pin.OUT,value=0)
            Pin(bme_pos,Pin.OUT,value=1)
            time.sleep_ms(200)

            # set up i2c bus
            bus = bus_i2c.I2CBUS(scl=i2c_scl,sda=i2c_sda,freq=i2c_frq)
            addrs = bus.scan()
            print('I2C DEVICES:',len(addrs),addrs)

            # set up bme
            bme = sensor_bme280.BME280(bus,address=118,altitude=bme_local_altitude,altitude_zero=False)            

            # function loop (loop forever)
            floops = 0
            while 1:

                print()
                
                # track loops
                floops += 1
                print('LOOP:',floops)

                # get bme280 data
                bme.force() # leave sleep, make conversion, go back to sleep
                if bme_weather_us:
                    temp,pres,humi = [round(x,2) for x in bme.weather_us()]
                else:
                    temp,pres,humi = [round(x,2) for x in bme.weather()]
                print('DATA:',[temp,pres,humi])

                # post data to eziot
                eziot.post_data(group=eziot_group,device=eziot_device,data1=temp,data2=pres,data3=humi,data4=None)
                print('LOADED to EZIOT')

                # wait for next loop
                # you may want to add deep sleep here
                print('Sleeping for 10 minutes.')
                time.sleep(600)

                # instead of just waiting, blink an LED on pin2
                #for x in range(150):
                #    Pin(2,Pin.OUT,value=1)
                #    time.sleep_ms(200)
                #    Pin(2,Pin.IN)
                #    time.sleep_ms(3800)
                    

        # end loop
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            break # end loop

        # error (show and retry, never end)
        except Exception as e:
            sys.print_exception(e)
            print('Major ERROR in main loop.')
            print('Pause 10 seconds...',end=' ')
            time.sleep(10)
            print('continue.')

#-----------------------
# self run
#-----------------------

if __name__ == '__main__':
    run()

#-----------------------
# end
#-----------------------
