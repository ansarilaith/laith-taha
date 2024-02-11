# example using eziot.link/dns and microserver
# originally by claytondarwin@gmail.com

# this is what runs beaker's server

#-------------------------------
# variables
#-------------------------------

# network credentials
essid    = 'youressid'
password = 'yourpassword'

# eziot credentials
eziot_api_key = 'yourkey'
eziot_api_secret = 'yoursecret'
eziot_dnsid = 'yourdnsid'

# server editor credentials
server_edpw = 'youreditorpassword'

#-------------------------------
# imports
#-------------------------------

# general
import time
import os
import sys
from machine import Pin

# hardware
from wlan import STA
from beeper import MINIBEEP
from pixels import PIXELS
from sdcard import SLOT2

# server
from microserver import MicroServer
import eziot_micropython_minimal as eziot

#-------------------------------
# create hardware objects
#-------------------------------

# these are required by local class/functions

# wifi
wifi = STA()

# beeper
beeper = MINIBEEP(2)
beeper.vol = 50

# pixels
pixels = PIXELS(4,8)

# sdcard (mounted below)
sdcard = SLOT2()
sdcard.slot =  3 
sdcard.cs   = 27 # non-standard funboard v1
sdcard.sck  = 14 # default slot 3
sdcard.mosi = 13 # default slot 3
sdcard.miso = 12 # default slot 3

# hard reset
def reset():
    p = Pin(15,Pin.OUT,value=0)
    p.value(0)

#-------------------------------
# create server with application
#-------------------------------

class SERVER(MicroServer):

    # server variables
    htdocs = '/sd/htdocs'
    do_cache = False
    poll_timeout = 2
    edpw = 'okay'

    # guest data
    guestfile = '/sd/guests.csv'
    guestlist = []
    guestread = False
    guestcount = 0
    guestshow = 24

    # guestlist reader
    def guestreader(self,lineno=None):

        # no file
        if not self.isfile(self.guestfile):
            print('FILE READ ERROR: NO FILE',self.guestfile)
            if lineno:
                return ['']*6

        # update
        guestcount = 0
        guestshow = self.guestshow
        guestlist = []

        # most-recent last
        with open(self.guestfile,'r') as f:
            for guest in f:
                guest = [x.strip() for x in guest.split('|')[:6]]
                if len(guest) == 6 and guest[0].isdigit():
                    # target line
                    if lineno == guest[0]:
                        return guest[:6]
                    guestcount = int(guest[0])
                    guestlist.append(tuple(guest[:6]))
                    guestlist = guestlist[-guestshow:]
            
        # target line not found
        if lineno:
            print('LINE LOOKUP FAILED')
            return ['']*6

        # most-recent first
        guestlist.reverse()
        self.guestlist = guestlist
        self.guestcount = guestcount
        self.guestread = True

    # guestlist update
    def guestwrite(self,data,new=False,delete=False):

        try:

            # data
            data = [str(x).strip() for x in data]
            if new and data[0] in ('','0','None'):
                self.guestcount += 1
                data[0] = str(self.guestcount)

            # new line
            if new:
                with open(self.guestfile,'a') as f:
                    f.write('{}|{}|{}|{}|{}|{}\n'.format(*data))
                    f.close()

            # update line
            elif data[0] and self.isfile(self.guestfile):

                # temp file
                guestfile2 = self.guestfile+'.temp'

                # make a backup
                t1 = time.ticks_ms()
                print('GUEST BACKUP:',end=' ')
                with open(self.guestfile) as f1:
                    with open(guestfile2,'w') as f2:
                        for guest in f1:
                            f2.write(guest)
                        f2.close()
                    f1.close()
                print('DONE',time.ticks_diff(time.ticks_ms(),t1))

                # make modified version from backup
                t1 = time.ticks_ms()
                print('GUEST UPDATE:',end=' ')
                guestcount = 0
                with open(guestfile2) as f1:
                    with open(self.guestfile,'w') as f2:
                        for guest in f1:
                            guest = [x.strip() for x in guest.split('|')[:6]]
                            if len(guest) == 6:
                                if guest[0] == data[0]:
                                    if delete:
                                        continue
                                    guest = data
                                guestcount += 1
                                guest[0] = str(guestcount)
                                f2.write('{}|{}|{}|{}|{}|{}\n'.format(*guest))
                        f2.close()
                    f1.close()
                print('DONE',time.ticks_diff(time.ticks_ms(),t1))

                # reload
                t1 = time.ticks_ms()
                print('GUEST RELOAD:',end=' ')
                self.guestreader()
                print('DONE',time.ticks_diff(time.ticks_ms(),t1))

            # done
            return data[0]

        except Exception as e:
            sys.print_exception(e)
            print('FILE WRITE ERROR:',self.guestfile)
            return '0'

    # shortcut for application
    def make_response(self,content='Hello World',codestring='200 OK',content_type='text/plain'):
        content = str(content)
        header = 'HTTP/1.1 {}\nContent-Type: {}\nContent-Length: {}\n\n'.format(codestring,content_type,len(content))
        return bytes(header+content,'utf8')

    #-------------------------------
    # redefine microserver functions
    #-------------------------------

    # called when server starts
    def server_init(self):

        # read guests
        self.guestreader()
        print('GUEST INIT:',self.guestcount)

    # called when client connects
    def client_on(self,rc=None):
        # rc = remote connection count
        #pass
        beeper.beep(vol=50)
        pixels.setp(0,'green',write=True)

    # called when client disconnects
    def client_off(self,path=None):
        # path = request PATH_INFO
        #pass
        pixels.off()

    # re-defining the application function
    def application(self,client_data,client_address,client_count):

        try:

            # get app option
            option = None
            if client_data['PATH_INFO']:
                option = client_data['PATH_INFO'].split('/')[-1].lower().strip()

            # pagecount option
            if option == 'pagecount':
                pixels.setp(7,'blue',write=True)
                yield self.make_response(client_count)

            # guestlist
            elif option == 'guestlist':
                pixels.setp(6,'green',write=True)

                # read file into guestlist (if it hasn't been done)
                if not self.guestread:
                    self.guestreader()

                # table parts
                table1 = '<table>'
                table2 = '\n</table>\n'
                line = '\n<tr><td class="c1">{}</td><td class="c2">{}</td><td class="c3">{}</td><td class="c4">{}</td><td class="c5">{}</td><td class="c6">{}</td></tr>'

                # work in blocks to save memory

                # content length
                cl = len(table1) + len(table2)
                for guest in self.guestlist:
                    cl += len(line.format(*guest))

                # header and table1
                yield bytes('HTTP/1.1 200\nContent-Type: text/plain\nContent-Length: {}\n\n{}'.format(cl,table1),'utf8')

                # lines
                for guest in self.guestlist:
                    yield bytes(line.format(*guest),'utf8')

                # end table2
                yield bytes(table2,'utf8')

            # guest
            elif option == 'guest':
                pixels.setp(5,'sun',write=True)

                # register
                name = client_data.get('name',[''])[0].replace('|',' ')[:32].strip()
                if name:
                    # build
                    home = client_data.get('from',[''])[0].replace('|',' ')[:32].strip()
                    mesg = client_data.get('mesg',[''])[0].replace('|',' ')[:64].strip()
                    date = wifi.dtstamp.split()[0]
                    self.guestcount += 1
                    data = (self.guestcount,date,name,home,mesg,'')
                    # save to guestlist (most-recent first)
                    self.guestlist.insert(0,data)
                    if len(self.guestlist) > self.guestshow:
                        self.questlist = self.guestlist[:self.guestshow]
                    # save to file (most-recent last)
                    self.guestwrite(data,new=True)

                # redirect (this resets the browser path too)
                # but it does make an additional request 
                content = '307 Temporary Redirect'
                location = '\nLocation: /index.html'
                yield self.make_response(content,content+location)

            # edit
            elif option == 'edit':
                pixels.setp(4,'orange',write=True)

                # check password first
                edpw = client_data.get('pw',[''])[0]
                if self.edpw and self.edpw != edpw:
                    content = '501 Not Implemented'
                    yield self.make_response(content,content)

                # get data
                save = client_data.get('save',[False])[0]
                line = client_data.get('line',[''])[0][:8]
                date = client_data.get('date',[''])[0][:10]
                name = client_data.get('name',[''])[0][:16]
                home = client_data.get('home',[''])[0][:24]
                mesg = client_data.get('mesg',[''])[0][:62]
                resp = client_data.get('resp',[''])[0][:62]

                # parse/fix
                if (not line) or (not line.isdigit()):
                    line = ''
                if resp == '!!!DELETE!!!':
                    delete = True
                else:
                    delete = False
                status = ''

                # save function
                if save == '1' and line:
                    line2 = self.guestwrite((line,date,name,home,mesg,resp),delete=delete)
                    if line != line2:
                        status = ' <span class="r">ERROR:{}<span>'.format((line,line2))
                    else:
                        if delete:
                            status = ' <span class="o">DELETE:{}</span>'.format(line2)
                        else:
                            status = ' <span class="g">SAVED:{}</span>'.format(line2)
                        save,line,date,name,home,mesg,resp = '','','','','','',''

                # data lookup
                if line and not name:
                     line,date,name,home,mesg,resp = self.guestreader(line)
                     status += ' <span class="g">LOOKUP:{}</span>'.format(line)

                # html form page
                # keep small, work in blocks to save memory

                # start block
                start = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Beaker's ESP32 Web Server EDIT</title>
<style>
@import url('https://fonts.googleapis.com/css?family=Short+Stack');
body {
background-color: black;
color: silver;
text-align: center;
font-size: 1em;
font-family: "Short Stack", monospace;
}
div {
display: block;
background-color: inherit; 
text-align: left;
border: solid silver 1px; 
margin: 8px auto;
padding: 8px;
}
td.c1 {color: #FFA150}
td.c2 {color: #82D182}
span.r {color: #FF3333}
span.o {color: #FFA150}
span.g {color: #82D182}
</style>
</head>
<body>
<div class="main" style="width: 720px">'''

                # status div
                status = '''
Beaker's ESP32 Web Server <span class="o">EDITOR</span>
<div>
STATUS: {}
</div>
'''.format(status.strip() or None)

                # lookup form div
                form1 = '''
<div class="form">
<form method="POST" action="/app/edit">
<input type="hidden" id="pw" name="pw" value="{}" />
Line: <input type="text" name="line" maxlength="4" size="4" value="{}"> <input type="submit" value="FIND">
</form>
</div>'''.format(edpw,line)
                
                # modify form div
                form2 = '''
<div class="form">
<form method="POST" action="/app/edit">
<input type="hidden" id="pw" name="pw" value="{}" />
<input type="hidden" id="save" name="save" value="1" />
<input type="hidden" id="line" name="line" value="{}" />
<input type="hidden" id="date" name="date" value="{}" />
<table>
<tr><td>Line:</td><td class="c1">{}</td></tr>
<tr><td>Date:</td><td><input type="text" name="date" maxlength="10" size="10" value="{}"></td></tr>
<tr><td>Name:</td><td><input type="text" name="name" maxlength="30" size="30" value="{}"></td></tr>
<tr><td>Home:</td><td><input type="text" name="home" maxlength="30" size="30" value="{}"></td></tr>
<tr><td>Mesg:</td><td><input type="text" name="mesg" maxlength="60" size="60" value="{}"></td></tr>
<tr><td>Resp:</td><td><input type="text" name="resp" maxlength="60" size="60" value="{}"></td></tr>
<tr><td>     </td><td><input type="submit" value="UPDATE"></td></tr>
</table>
</form>
</div>'''.format(edpw,line,date,line,date,name,home,mesg,resp)

                # end block
                end = '\n</div>\n</body>\n</html>\n'

                # content length
                cl = len(start)+len(status)+len(form1)+len(form2)+len(end)

                # send
                yield bytes('HTTP/1.1 200\nContent-Type: text/html\nContent-Length: {}\n\n'.format(cl),'utf8')
                yield bytes(start,'utf8')
                yield bytes(status,'utf8')
                yield bytes(form1,'utf8')
                yield bytes(form2,'utf8')
                yield bytes(end,'utf8')

            # not implemented
            else:
                pixels.setp(1,'red',write=True)
                content = '501 Not Implemented'
                yield self.make_response(content,content)

        except Exception as e:
            pixels.setp(0,'red',write=True)
            import sys
            sys.print_exception(e)
            content = '500 Internal Server Error'
            yield self.make_response(content,content)        

#-------------------------------
# create dns+rtc update thread
#-------------------------------

class DNS():

    running = False
    kill = False
    thread = None

    def start(self):
        self.stop()
        print('EZIoT DNS START')
        self.kill = False
        import _thread
        self.thread = _thread.start_new_thread(self.run,())
        del _thread
        for x in range(10):
            if self.running:
                return True
            time.sleep_ms(100)
        print('EZIoT DNS START:',self.running)
        return self.running

    def run(self):
        try:
            eziot.api_key = eziot_api_key
            eziot.api_secret = eziot_api_secret
            self.running = True
            lc = 0
            while 1:

                if self.kill:
                    break

                # dns update (1 loop == 10 mins)
                dnsid = None
                for x in range(10):
                    if self.kill:
                        break
                    try:
                        dnsid = eziot.set_dns(dnsid=eziot_dnsid)
                        break
                    except:
                        time.sleep_ms(1000)
                print('EZIoT DNS:',dnsid == eziot_dnsid.upper())

                # check clock
                wifi.set_rtc(tries=10,only_if_needed=True)
                print('EZIoT RTC:',wifi.dtstamp)

                # force clock update (144 loops == 24 hours)
                if lc >= 144:
                    wifi.set_rtc(tries=10,only_if_needed=False)
                    lc = 0

                # loop time (600 secs == 10 mins)
                for x in range(600):
                    if self.kill:
                        break
                    time.sleep_ms(1000)
                lc += 1

        except Exception as e:
            sys.print_exception(e)
        self.running = False
        print('EZIoT DNS END')    

    def stop(self):
        print('EZIoT DNS STOP')
        self.kill = True
        for x in range(10):
            if not self.running:
                return True
            time.sleep_ms(1000)
        return not self.running

#-------------------------------
# 
#-------------------------------

def run():

    print('MAIN:')

    # make server instance
    server = SERVER()

    # make eziot instance
    dns = DNS()

    print('MAIN: start loop')

    while 1:

        try:

            # sdcard
            sdcard.unmount()
            sdcard.mount()

            # network
            try:
                assert wifi.connect(essid,password)
            except:
                print('Waiting on wifi connect.')
                time.sleep_ms(1000)
                continue

            # eziot dns+rtc update thread
            if not dns.running:
                dns.start()

            # start server
            # loop stops here until failure
            server.serve()

            # cascade KeyboardInterrupt
            if server.keyboard_interrupt:
                raise KeyboardInterrupt

            # pause
            time.sleep_ms(1000)

        # keyboard kill
        except KeyboardInterrupt:
            print('MAIN: KeyboardInterrupt: end all')
            break

        # any exception
        except Exception as error:
            print('MAIN: reset')
            sys.print_exception(error)

    # kill dns
    dns.stop()

    # done
    print('MAIN: end')

# start loop
if __name__ == '__main__':
    run()

#-------------------------------
# end
#-------------------------------
