#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# general imports
#-----------------------

import time

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
    eziot.wifi_connect('your_essid','your_password')  

    # add credentials for example data table
    # to get your own credentials: eziot.get_creds()
    eziot.api_key = 'EXAMPLE'
    eziot.api_secret = 'EXAMPLE'

    # get current stats
    print()
    stats = eziot.stats()
    keys = list(stats.keys())
    keys.sort()
    for key in keys:
        print('STAT:',[key,stats[key]])
    del stats,keys,key

    # get+print 10 most-recent data rows
    print()
    for row in eziot.get_data(10):
        print('ROW:',row)

    # add data row
    print()
    rowid = eziot.post_data('clayton','funboard-1','hello',123,456789,'cats and dogs')
    print('LOADED ROWID:',[rowid])

    # get+print 10 most-recent data rows
    print()
    for row in eziot.get_data(10):
        print('ROW:',row)

    # delete your row
    print()
    deletes = eziot.delete_data(rowid)
    print('DELETED ROWS:',[deletes])
    
    # get+print 10 most-recent data rows
    print()
    for row in eziot.get_data(10):
        print('ROW:',row)

    # disconnect from wifi access point
    print()
    eziot.wifi_disconnect()

    # done
    print('\nScript "example.py" complete.\n')

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
