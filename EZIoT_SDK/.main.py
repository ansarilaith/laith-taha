#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# general imports
#-----------------------

import time
import random

#-----------------------
# testing catch
#-----------------------

try:

    #-----------------------
    # eziot examples
    #-----------------------

    # import
    import eziot

    # scan for wifi access points
    print()
    eziot.wifi_scan()

    # connect to wifi access point
    print()
    eziot.wifi_connect('DARWIN-NET-TEST','claytondarwin')  

    # add credentials for example data table
    # to get your own credentials: eziot.get_creds()
    eziot.api_key = 'EXAMPLE'
    eziot.api_secret = 'EXAMPLE'
    eziot.api_key = 'CLAYTONKEY'
    eziot.api_secret = 'CLAYTONSECRET'

    # loop post
    x = 0
    while 1:
        x += 1
        count = random.randint(2,200)
        word = random.choice('cats dogs pigs chickens pickles mice unicorns dragons monkeys llamas krakens paramecium'.split())
        rowid = eziot.post_data('clayton','funboard-1','hello',x,data4='i have detected {} {}'.format(count,word))
        print('LOADED:',[x,count,word])
        time.sleep(60)    

#-----------------------
# end testing catch
#-----------------------

except KeyboardInterrupt:
    print('Keyboard Interrupt: main.py ending.')
    
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Exception: main.py ending.')

#-----------------------
# end
#-----------------------
