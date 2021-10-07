#-----------------------------------------------
# notes
#-----------------------------------------------

# microserver.py is a small server for MicroPython
# this was originally written by claytondarwin@gmail.com
# clayton does not care what you do with it

# REQUIRES:
# wifi connection exists

# LIMITS:
# does not take advantage of async functions
# header lines <= 256 characters
# input <= 1024 characters
# not set up for https (but you could ssl-wrap the client socket)
# only handles common static file types (everything else is application/octet-stream)

# APPLICATION:
# you define (re-define) the application
# if path startswith /app/, application is called
# user-defined application MUST accept 3 values
# user-defined application MUST be an interator
# user-defined application MUST return full content (header+data)
# user-defined application MUST return bytes
# application(client_data,client_address,client_count)
# client_data is a dict of item:value pairs
# client_address is a tuple where index 0 is the client ip
# client_count is the total number of client connections since restart

# TEAPOT:
# If a client asks for a non-existing path, assume they are fishing.
# Send code 418 "I'm a teapot." and block the client IP for "teapot_lockout" seconds.
# This reduces overhead and bandwith from fishing and crawlers.

#-----------------------------------------------
# setup
#-----------------------------------------------

# notify
print('LOAD: microserver.py')

# imports
import os,sys,time,network,gc,socket
from uselect import poll,POLLIN,POLLHUP,POLLERR
gc.collect()

#-----------------------------------------------
# class
#-----------------------------------------------

class MicroServer:

    #-------------------------------------------
    # variables
    #-------------------------------------------

    # user-defined variables
    host = '0.0.0.0'
    port = 80
    https = False
    max_requests = 5 # client sockets
    max_content = 1024 # from client socket
    socket_timeout = 30 # client socket
    teapot_lockout = 20 # bad client lockout
    htdocs = '/htdocs'

    # static file cache directives
    # seconds for client to cache files/images
    cache_for = 60*60*24 # = 24 hours
    # non-cached files (send no-cache header)
    nocache = ['/index.html']

    # process variables
    keyboard_interrupt = False # loop ended on a KeyboardInterrupt
    rc = 0 # client connection count
    kill = False # kill server loop   
    poll_timeout = 10 # seconds when polling client socket

    #-------------------------------------------
    # applications
    #-------------------------------------------

    # user-defined applications
    # these are placeholders and should be replaced

    # application MUST accept three input values
    # application MUST be an iterator (use yield instead of return)
    # application MUST yield the full response (header + data)
    # the response MUST be bytes
    def application(self,client_data,client_address,client_count):

        data = 'Client {} at {}.\nNo user application is defined.\n\n'.format(client_count,client_address[0])
        data = bytes(data,'latin1')

        header = 'HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: {}\n\n'.format(len(data))

        yield bytes(header,'latin1') + data

    # called when client connects
    def client_on(self,rc=None):
        # rc = remote connection count
        pass

    # called when client disconnects
    def client_off(self,path=None):
        # path = request PATH_INFO
        pass
    
    #-------------------------------------------
    # server (serve forever)
    #-------------------------------------------

    def serve(self):

        # check server address outside of loop and catch
        self.server_address = socket.getaddrinfo(self.host,self.port)[0][-1]

        # record keyboard interrupt
        keyboard_interrupt = False

        # restart forever (except KeyboardInterrupt or self.kill == True)
        while 1:

            # catch all
            try:

                # open server socket
                server_socket = socket.socket()
                server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                server_socket.bind(self.server_address)
                server_socket.listen(self.max_requests)
                print('uServer socket listening +{} on addr {}.'.format(self.max_requests,self.server_address))

                # last bad client address and time
                teapot = (None,0)

                # accept request loop
                while 1:

                    # kill flag
                    if self.kill:
                        print('uServer KILL flag set.')
                        break

                    # accept a request
                    # get client socket (i.e. request socket)
                    client_socket,client_address = server_socket.accept()
                    t1 = time.ticks_ms()
                    now = '{}-{}-{}_{}:{}:{}'.format(*time.localtime()[:6])
                    self.rc += 1

                    # teapot = do nothing and allow close
                    if client_address[0] == teapot[0] and time.ticks_diff(t1,teapot[1]) < self.teapot_lockout*1000:
                        print('uServer Teapot {}: {} - {} - M{}%.'.format(self.rc,client_address[0],now,self.memp()))
                        teapot[1] = t1

                    # non-teapot (good client)
                    else:

                        # clear teapot
                        teapot = (None,0)

                        # start client                        
                        self.client_on(self.rc)
                        client_socket.settimeout(self.socket_timeout) # 0
                        print('uServer Client {}: {} - {} - M{}%.'.format(self.rc,client_address[0],now,self.memp()))
                        bytecount = 0

                        # parse all input data
                        client_data = self.parse_socket_data(client_socket,client_address)
                        print('uServer Client {} REQUEST: {} {} {} {} {}'.format(
                            self.rc,
                            client_data['SERVER_PROTOCOL'],
                            client_data['REQUEST_METHOD'],
                            client_data['PATH_INFO'],
                            client_data['Content-Length'],
                            client_data['Content-Type'],
                            ))

                        # path
                        path = client_data['PATH_INFO'] or '/index.html'
                        if path == '/':
                            path = '/index.html'

                        # static file
                        if path and self.isfile(self.htdocs+path):
                            cache = not (path in self.nocache)
                            print('    File Request: {}'.format(path))
                            for block in self.file_server(self.htdocs+path,cache=cache):
                                bytecount += client_socket.write(block)

                        # application iterator
                        elif path and path[:5] in ('/app','/app/'):
                            print('    Application Request')
                            for block in self.application(client_data,client_address,self.rc):
                                bytecount += client_socket.write(block)

                        # unknown (bad client)
                        else:
                            print("    Unknown Request: I'm a teapot.")
                            teapot = [client_address[0],t1]
                            bytecount += client_socket.write(bytes("HTTP/1.1 418 I'm a teapot.\nContent-Type: text/plain\nContent-Length: 19\n\n418 I'm a teapot.\n",'utf8'))

                        # end client
                        self.client_off(path)
                        print('uServer Client {}: {} - M{}% - {} bytes in {} secs.'.format(self.rc,client_address[0],self.memp(),bytecount,round(time.ticks_diff(time.ticks_ms(),t1)/1000.0,2)))

                    # close client socket
                    client_socket.close()
                    gc.collect()
                    
            # keyboard kill
            except KeyboardInterrupt:
                keyboard_interrupt = True
                print('uServer KeyboardInterrupt: End server loop.')
                break

            # any other exception
            except Exception as error:
                print('uServer Exception: Go to socket reset.')
                sys.print_exception(error)

            # must do
            finally:

                # close main socket
                try:
                    print('uServer Closing main socket...',end=' ')
                    server_socket.close()
                    print('closed.')
                except:
                    print('uServer FAILED!')

                # clean up
                self.client_off()
                gc.collect()
 
    #-------------------------------------------
    # server sub-functions
    #-------------------------------------------

    def memp(self,collect=False):
        if collect:
            gc.collect()
        free  = gc.mem_free()
        alloc = gc.mem_alloc()
        size = free+alloc
        return int(round(100*alloc/size,0))

    def isfile(self,f):
        try:
            stats = os.stat(f)
            if oct(stats[0])[-5] != '4':
                return True
            else:
                return False
        except:
            return False

    def file_server(self,path,cache=False):

        # file must exist
        # ext-based file type

        ext = None
        if '.' in path:
            ext = path.rsplit('.',1)[1].lower()

        # make header
        header  = 'HTTP/1.1 200 OK\n'
        if cache is True:
            header += 'Cache-Control: max-age={}\n'.format(self.cache_for)      
        elif cache in (None,0):
            header += 'Cache-Control: no-cache\n'
        elif type(cache) == int and cache > 0:
            header += 'Cache-Control: max-age={}\n'.format(cache)
        header += 'Content-Type: {}\n'.format(self.file_types.get(ext,'application/octet-stream'))
        header += 'Content-Length: {}\n'.format(os.stat(path)[6])

        # send header
        yield bytes(header+'\n','utf8')

        # send file
        with open(path,'rb') as f:
            while 1:
                data = f.read(1024)
                if data:
                    yield data
                else:
                    break
            f.close()

    file_types = {
    'html':'text/html',
    'css':'text/css',      
    'txt':'text/plain',
    'csv':'text/plain',      
    'json':'application/json',
    'pdf':'application/pdf',
    'ico':'image/x-icon',
    'jpg':'image/jpeg',
    'png':'image/png',
    'svg':'image/svg+xml',
    'gif':'image/gif',
    }

    def parse_socket_data(self,client_socket,client_address,show=True):

        # register client socket
        poller = poll()
        poller.register(client_socket,POLLIN)

        # start query data
        query_data =  {
        'REMOTE_ADDR':client_address[0],
        'SERVER_PROTOCOL':None,
        'REQUEST_METHOD':None,
        'PATH_INFO':None,
        'Content-Length':0,
        'Content-Type':None
        }

        # read header lines up to '\n\n'
        # add each line into query_data
        while 1:
            polldata = poller.poll(int(self.poll_timeout*1000))
            line = None
            if not polldata:
                print('  HEADER <NO_DATA>')
                break
            elif polldata[0][1] in (POLLHUP,POLLERR):
                print('  HEADER <POLLHUP_POLLERR>')
                break
            else:
                line = client_socket.readline()[:256]
                if not line or line == b'\r\n':
                    break
                if show:
                    print('  HEADER_LINE:',[line[:96]])
                line = line.decode('utf8','replace').strip()
                # GET
                if line.startswith('GET '):
                    query_data['REQUEST_METHOD'] = 'GET'
                    line = line.split()
                    if len(line) >= 3:
                        query_data['SERVER_PROTOCOL'] = line[2]
                        path = line[1]
                        if '?' in path:
                            path,qs = path.split('?',1)
                            self.parse_content(qs,query_data)
                        path = path.strip()
                        query_data['PATH_INFO'] = path
                # POST
                elif line.startswith('POST '):
                    query_data['REQUEST_METHOD'] = 'POST'
                    line = line.split()
                    if len(line) >= 3:
                        query_data['SERVER_PROTOCOL'] = line[2]
                        query_data['PATH_INFO']       = line[1]
                # Content-Length:
                elif line.startswith('Content-Length'):
                    line = line.split()
                    if len(line) >= 2 and line[1].isdigit():
                        query_data['Content-Length'] = int(line[1])
                # Content-Type:
                elif line.startswith('Content-Type'):
                    line = line.split()
                    if len(line) >= 2:
                        query_data['Content-Type'] = ' '.join(line[1:])

        # handle a POST (extra data)
        if query_data['REQUEST_METHOD'] == 'POST':
            # multipart
            if 'multipart' in query_data['Content-Type']:
                pass
            # no content length
            elif not query_data['Content-Length']:
                pass
            # read data
            else:
                clen = query_data['Content-Length']
                if self.max_content:
                    clen = min(clen,self.max_content)
                dlen = 0
                data = b''
                while dlen < clen:
                    polldata = poller.poll(int(self.poll_timeout*1000))
                    if not polldata:
                        print('  POST <NO_DATA>')
                        break
                    elif polldata[0][1] in (POLLHUP,POLLERR):
                        print('  POST <POLLHUP_POLLERR>')
                        break
                    else:
                        data += client_socket.recv(clen-dlen)
                        dlen = len(data)
                self.parse_content(data,query_data)

        # un-register client socket
        poller.unregister(client_socket)
        del poller

        # print data
        if show:
            keys = list(query_data.keys())
            keys.sort()
            for key in keys:
                print('  INPUT:',key,str(query_data[key])[:96])
            del keys           

        # done
        return query_data

    def parse_content(self,content,qd,final=False):

        # decode
        if type(content) == bytes:
            content = content.decode('utf8','replace')

        # split into parts on &
        if '&' in content:
            parts = content.split('&')
        else:
            parts = [content]

        # clean
        del content
        gc.collect()

        # parse parts to qd
        for part in parts:
            if part:
                key,value = (part.split('=',1)+[''])[:2]
                if key.strip():
                    value,rest = self.url_unquote(value)
                    if key in qd:
                        qd[key].append(value)
                    else:
                        qd[key] = [value]

    def url_unquote(self,text):

        # replace url escape sequences in text
        # return unquoted_text,remaining_text
        # the remaining_text can be added to the next block

        # the remaining_text is 0 to 2 chars in length
        # this text is missing necessary characters
        # i.e. the input text ended with % or %X, not %XX

        rest = ''
        if '%' in text[-2:]:
            rest = text[-2:]
            text = text[:-2]

        if '+' in text:
            text = text.replace('+',' ')

        while '%' in text:
            i = text.index('%')
            c1 = text[i:i+3]
            c2 = self.url_unquote_values.get(c1,'?')
            text = text.replace(c1,c2)

        return text,rest

    # url unquote values
    url_unquote_values = {
    '%0D':'\r',
    '%0A':'\n',
    '%20':' ',
    '%21':'!',
    '%22':'"',
    '%23':'#',
    '%24':'$',
    '%25':'%',
    '%26':'&',
    '%27':"'",
    '%28':'(',
    '%29':')',
    '%2A':'*',
    '%2B':'+',
    '%2C':',',
    '%2D':'-',
    '%2E':'.',
    '%2F':'/',
    '%3A':':',
    '%3B':';',
    '%3C':'<',
    '%3D':'=',
    '%3E':'>',
    '%3F':'?',
    '%40':'@',
    '%5B':'[',
    '%5C':'\\',
    '%5D':']',
    '%5E':'^',
    '%5F':'_',
    '%60':'`',
    '%7B':'{',
    '%7C':'|',
    '%7D':'}',
    '%7E':'~',
    }

#-----------------------------------------------
# end
#-----------------------------------------------
