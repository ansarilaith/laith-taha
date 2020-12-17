# nettools_wget.py = adds wget function, requires more imports
# Copyright (c) 2019 Clayton Darwin
# claytondarwin.com claytondarwin@gmail.com

# NOTE: these functions/classes require a network connection
# see nettools.py for options/suggestions

# notify
print('LOAD: nettools_wget.py')

# imports
import time,network,gc
import socket, ssl # actually imports usocket and ussl
from uselect import poll,POLLIN,POLLHUP,POLLERR
gc.collect()
  
# make a GET request to URL
def wget(url,outfile=None,show_data=False,return_data=True,max_data=10240):

    # MUST be connected to a network AP first

    # url         = [http[s]://]host[:port][/path][?variables] = only host is required
    #               HTTPS must start URL with "https://" or specify port 443
    # outfile     = write return data to this file, None = don't
    # show_data   = print return data to stdout, False = don't
    # return_data = keep data in memory and return at end of function
    # max_data    = maximum content length to keep in bytes

    # return = if return_data = ([list or (header,value) tuples],b'content as bytes')
    #                    else = ([],b'')

    # clear memory
    gc.collect()

    # get address variables
    http = 'http'
    if '://' in url:
        http,url = url.split('://',1)
    host = url.split('?')[0].split('/')[0]
    path = url[len(host):].strip('/')

    # set port
    port = 80
    if http == 'https':
        port = 443
    if ":" in host:
        host,port = host.split(':',1)
        port = int(port)
    if show_data:
        print('-'*48)
        print('WGET:',[http,host,port,path])

    # open output
    if outfile:
        o = open(outfile,'wb')

    # make socket
    s = socket.socket()
    s.connect(socket.getaddrinfo(host,port,0,socket.SOCK_STREAM)[0][-1])
    s.setblocking(False)

    # make ssl
    if http == 'https' or port == 443:
        s = ssl.wrap_socket(s)

    # write GET request
    s.write(b'GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(path,host))

    # set up polling
    poller = poll()
    poller.register(s,POLLIN)

    # read headers
    headers = []
    content_len = 1 # will get at least 1 read if cl not specified
    if show_data:
        print('-'*48)
    while 1:
        polldata = poller.poll(10000) # initial timeout in ms
        if not polldata:
            if show_data:
                print('\n<NO_DATA>')
            break
        elif polldata[0][1] in (POLLHUP,POLLERR):
            if show_data:
                print('\n<POLLHUP_POLLERR>')
            break
        else:
            line = s.readline()[:256]
            if not line or line == b'\r\n':
                if outfile:
                    o.write(b'\r\n')
                if show_data:
                    print()
                break
            else:
                if return_data:
                    headers.append(line.strip())
                if outfile:
                    o.write(line)
                if show_data:
                    print('HEADER:',line)
                if line.startswith(b'Content-Length:'):
                    line = line[15:].strip()
                    if line.isdigit():
                        content_len = int(line)
            del line
        del polldata

    # read content
    data = b''
    data_len = 0
    content_len = min(content_len,max_data)
    if show_data:
        print('-'*48)
        print('DATA:',content_len)
    while data_len < content_len:
        polldata = poller.poll(1000) # 1 sec timeout post headers
        if not polldata:
            if show_data:
                print('\n<END_OF_DATA>')
            break
        elif polldata[0][1] in (POLLHUP,POLLERR):
            if show_data:
                print('\n<POLLHUP_POLLERR>')
            break
        else:
            read = s.read()
            if return_data:
                data += read
            if outfile:
                o.write(read)
            if show_data:
                print(read,end='')
            data_len += len(read)
            del read
        del polldata

    # close output
    if show_data:
        print()
        print('-'*48)
    if outfile:
        o.close()

    # close socket
    s.close()

    # clear memory
    gc.collect()

    # done
    return headers,data


