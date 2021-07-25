# example using eziot.link/dns and microserver
# originally by claytondarwin@gmail.com

# this is what runs beaker's server

#-------------------------------
# variables
#-------------------------------

# network (add your credentials)
essid    = 'youressid'
password = 'yourpassword'

# eziot (add your credentials)
eziot_api_key = 'yourkey'
eziot_api_secret = 'yoursecret'
eziot_dnsid = 'yourdnsid'

#-------------------------------
# imports
#-------------------------------

import time
from microserver import MicroServer

#-------------------------------
# not using a funboard
#-------------------------------

# if you are not not using a funboard ...

# you need to do these imports
# import eziot

# you will need to create these functions
# wifi.connect(essid,password)
# rtc.ntp_set() is "from ntptime import settime"
# esp32.reset()

# you can comment out these (or replace with pass)
# beeper.beep()
# pixels.setp(0,'red')
# pixels.off()

# you will need to set up the /sd/htdocs dir
# you can do it on the esp32 of mount an sdcard

#-------------------------------
# create server with application
#-------------------------------

class SERVER(MicroServer):

    # server variables
    htdocs = '/sd/htdocs'

    # guest data
    guestfile = '/sd/guests.csv'
    guestlist = []
    guestread = False
    guestcount = 0
    guestshow = 24

    # redefine client thread open-close functions

    # called when client connects
    def client_on(self,rc=None):
        # rc = remote connection count
        #pass
        beeper.beep(vol=50)
        pixels.setp(0,'red')

    # called when client disconnects
    def client_off(self,path=None):
        # path = request PATH_INFO
        #pass
        pixels.off()

    # shortcut for application
    def make_response(self,content='Hello World',codestring='200 OK'):
        content = str(content)
        header = 'HTTP/1.1 {}\nContent-Type: text/plain\nContent-Length: {}\n\n'.format(codestring,len(content))
        return bytes(header+content,'utf8')

    # i'm re-defining the application function to do what i want
    def application(self,client_data,client_address,client_count):

        try:

            # get app option
            option = None
            if client_data['PATH_INFO']:
                option = client_data['PATH_INFO'].split('/')[-1].lower().strip()

            # pagecount option
            if option == 'pagecount':
                yield self.make_response(client_count)

            # guest
            elif option == 'guest':

                # register
                name = client_data.get('name',[''])[0].replace('|',' ')[:32].strip()
                if name:
                    where = client_data.get('from',[''])[0].replace('|',' ')[:32].strip()
                    mesg = client_data.get('mesg',[''])[0].replace('|',' ')[:64].strip()
                    now = rtc.dtstamp.split()[0]
                    self.guestcount += 1
                    self.guestlist.append((now,name,where,mesg))
                    if len(self.guestlist) > self.guestshow:
                        self.questlist = self.guestlist[-self.guestshow:]
                    with open(self.guestfile,'a') as f:
                        f.write('{}|{}|{}|{}\n'.format(now,name,where,mesg))
                        f.close()

                ## # send index
                ## for block in self.file_server(self.htdocs+'/index.html',cache=False):
                ##     yield block

                # redirect (this resets the browser path too)
                # but it does make an additional request 
                content = '307 Temporary Redirect'
                location = '\nLocation: /index.html'
                yield self.make_response(content,content+location)

            # guestlist
            elif option == 'guestlist':

                # read file
                if (not self.guestread) and self.isfile(self.guestfile):
                    guestcount = 0
                    guestshow = self.guestshow
                    guestlist = []
                    with open(self.guestfile,'r') as f:
                        for line in f:
                            line = line.split('|',3)
                            if len(line) == 4:
                                guestcount += 1
                                guestlist.append(tuple(line))
                                guestlist = guestlist[-guestshow:]
                    self.guestlist = guestlist
                    self.guestcount = guestcount
                    self.guestread = True

                # send data
                table = '\n<table>'
                for guest in self.guestlist[::-1]:
                    table += '\n<tr><td class="nw">{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(*guest)
                table += '\n<tr><td class="nw" colspan="4">Total Guests: {}</td></tr>'.format(self.guestcount)
                table += '\n</table>\n'                
                yield self.make_response(table)

            # not implemented
            else:
                content = '501 Not Implemented'
                yield self.make_response(content,content)

        except Exception as e:
            import sys
            sys.print_exception(e)
            content = '500 Internal Server Error'
            yield self.make_response(content,content)        

# make server instance
server = SERVER()

#-------------------------------
# create a reboot thread
#-------------------------------

# this is optional - reboots daily

##import _thread
##
##def reboot_thread_function():
##
##    print('REBOOT THREAD: start')
##
##    reset_hour = 6 # gmt
##
##    # loop
##    loops = 0
##    while not reboot_thread_kill:
##
##        # gurrent gmt
##        y,M,d,h,m,s = time.gmtime()[:6]
##
##        # notify every 10 minutes
##        loops += 1
##        if loops >= 600:
##            loops = 0
##            H = reset_hour - h
##            if H < 0:
##                H += 24
##            print('REBOOT IN: {:0>2}hrs {:0>2}mins {:0>2}secs'.format(H,60-m,60-s))
##
##        # skip boot condition
##        if (y,M,d) != (2000,1,1):
##            # hour and minute correct 
##            if h,m == reset_hour,0:
##                # second is correct
##                if 0 <= s <= 10:
##                    print('REBOOT THREAD: reset')
##                    esp32.reset()
##
##        # pause
##        time.sleep_ms(100)
##        
##    print('REBOOT THREAD: end')
##        
##reboot_thread_kill = False
##reboot_thread = _thread.start_new_thread(reboot_thread_function,())

#-------------------------------
# loop forever
#-------------------------------

print('MAIN: start loop')

while 1:

    try:

        # network
        try:
            assert wifi.connect(essid,password)
        except:
            print('Waiting on wifi connect.')
            time.sleep_ms(1000)
            continue

        # set clock (may fail)
        for x in range(100):
            try:
                assert rtc.ntp_set()
                break
            except:
                pass

        # eziot dns register
        eziot.api_key = eziot_api_key
        eziot.api_secret = eziot_api_secret
        for x in range(10):
            try:
                dnsid = eziot.set_dns(dnsid=eziot_dnsid)
                print('EZIoT DNS:',dnsid)
                break
            except:
                time.sleep_ms(1000)

        # start server
        server.serve()

        # cascade KeyboardInterrupt
        if server.keyboard_interrupt:
            raise KeyboardInterrupt

        # pause
        time.sleep_ms(1000)

    # keyboard kill
    except KeyboardInterrupt:
        print('MAIN: KeyboardInterrupt: end all')
##        try:
##            reboot_thread_kill = True
##            reboot_thread.exit()
##        except:
##            pass
        break

    # any exception
    except Exception as error:
        print('MAIN: reset')
        sys.print_exception(error)

print('MAIN: end')


#-------------------------------
# end
#-------------------------------
