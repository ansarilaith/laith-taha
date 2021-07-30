import sys,time
from machine import UART

class SerialGPS:

    # this is for Ublox Neo 6 and Neo 8 using a serial port

    def __init__(self):
        pass

    # serial setup
    baudrate = 9600
    bits = 8
    parity = None
    stop = 1
    timeout = 1024 # micro seconds
    tx = 17
    rx = 16
    # add buffer sizes

    # time zone adjust (+- hours from utc)
    timezone = 0

    def port_open(self,port=1):

        # make port
        self.port = UART(port,baudrate=self.baudrate,bits=self.bits,parity=self.parity,stop=self.stop,timeout=self.timeout,tx=self.tx,rx=self.rx)

        # try a flush:
        self.port_flush()         

        # send NMEA-only message
        self.nmea_only()

        # drop (switch off) common messages
        #for name in 'GGA GLL GBS GNS GRS GSA GST GSV TXT '.split():
        for name in 'GGA GLL GBS GNS GRS GSA GST GSV TXT VGT ZDA'.split():
            self.nmea_message_switch(name,False)

        # get intended messages
        #for name in ('VTG','ZDA','RMC'):
        for name in ('RMC',):
            self.nmea_message_switch(name,True)

        # try a flush:
        self.port_flush()         

    def port_flush(self):
        
        self.port.read(self.port.any())

    def port_close(self):

        self.port.deinit()

        del self.port

    def get_data(self,timeout=2):

        # start time
        t1 = time.time()

        # start data (None = no data)
        # datetime = UTC (adjusted for self.timezone)
        # lat and long are degrees (float values)
        # minutes and seconds are converted to degrees in the decimal portion
        # negative lat is south
        # negative long is west
        # course is degrees
        #         0    1     2    3    4      5      6    7    8      9     10   11
        # data = [year,month,day ,hour,minute,second,lat ,long,course,knots,kph ,mph ]
        data   = [None,None ,None,None,None  ,None  ,None,None,None  ,None ,None,None]

        # get data, keep trying until RMC line read or timeout
        while 1:

            # catch
            try:

                # wait
                if not self.port.any():
                    time.sleep(0.1)
                    continue

                # get line
                line = self.port.readline()
                if line:

                    # initial parse
                    line,check = self.parse_nmea_bytes(line,check=False,numbers=False)
                    name = line[0][-3:]

                    # RMC
                    if name == 'RMC':
                        # NMEA: Ublox 8 specs  = 14 values =  $xxRMC,time  ,status,lat     ,NS,long     ,EW,knots,cog,date  ,mv,mvEW,posMode,navStatus*cs<CR><LF>
                        # NMEA: Ublox 6 specs  = 13 values =  $GPRMC,hhmmss,status,latitude,N ,longitude,E ,spd  ,cog,ddmmyy,mv,mvE ,mode             *cs<CR><LF>
                        if len(line) >= 10:
                            xxRMC,utc,status,lat,NS,long,EW,knots,cog,date = [x.strip() for x in line[:10]]

                            # date
                            isdate = False
                            if date and date[:6].isdigit():
                                data[2] = int(date[:2])
                                data[1] = int(date[2:4])
                                data[0] = int(date[4:6])+2000
                                isdate = True

                            # time
                            istime = False
                            if utc and utc[:6].isdigit():
                                data[3] = int(utc[:2])
                                data[4] = int(utc[2:4])
                                data[5] = int(utc[4:6])
                                istime = True

                            # time+date adjust
                            if self.timezone and istime:
                                if isdate:
                                    data[:6] = time.localtime(time.mktime(data[:6]+[None,None])+(self.timezone*3600))[:6]
                                else:
                                    data[3:6] = time.localtime(time.mktime([2000,1,1]+data[3:6]+[None,None])+(self.timezone*3600))[3:6]

                            # lat
                            if lat:
                                data[6] = int(lat[:2]) + float(lat[2:])/60
                                if NS == 'S':
                                    data[6] *= -1
                                
                            # long
                            if long:
                                data[7] = int(long[:3]) + float(long[3:])/60
                                if EW == 'W':
                                    data[7] *= -1

                            # course over ground (degrees)
                            if cog:
                                data[8] = float(cog)

                            # speed
                            if knots:
                                knots = float(knots)
                                data[9] = knots
                                data[10] = knots*1.852
                                data[11] = knots*1.150779

                            # full RMC line is success
                            break

                    # drop unused message types
                    elif len(name) == 3 and not name.isdigit():
                        print('EXTRA:',line)
                        self.nmea_only()
                        self.nmea_message_switch(name,False)

                    # ?
                    else:
                        print('ERROR:',line)

            # whatever
            except Exception as e:
                sys.print_exception(e)

            # check for timeout
            if time.time() - t1 >= timeout:
                print('DATA TIMEOUT')
                break

        # done (any False is an error)
        return data

    # NMEA: PUBX 41: change message protocols
    # 0002 = NMEA only
    def nmea_only(self):

        message = self.make_nmea_bytes('PUBX,41,1,0002,0002,9600,0')

        self.port.write(message)
        time.sleep(0.1)

    # NMEA: PUPX 40: turn on/off message types
    def nmea_message_switch(self,name,on=False):

        name = name[-3:]
        
        if on:
            message = self.make_nmea_bytes('PUBX,40,{},0,1,0,0,0,0'.format(name))
            print('ON:',name)

        else:
            message = self.make_nmea_bytes('PUBX,40,{},0,0,0,0,0,0'.format(name))
            print('OFF:',name)

        self.port.write(message)
        time.sleep(0.1)
        
    # make a NMEA string from string, numbers, list, or tuple
    def make_nmea_bytes(self,data):

        # lists and tuples
        if type(data) in (list,tuple):   
            data = ','.join([str(x).strip() for x in data])

        # others
        else:
            data = str(data).strip()

        return bytearray('$' + data + '*' + self.xor(data) + '\r\n','latin1','?')

    # parse a NMEA string to a list
    def parse_nmea_bytes(self,data,check=False,numbers=False):

        print('DATA:',data)

        string = data.decode('ascii','?')

        string = string.lstrip('$')

        string,checksum1 = (string+'*').split('*')[:2]

        data = []
        
        for x in string.split(','):

            if numbers:

                if x.isdigit():
                    x = int(x)

                elif x.replace('.','').isdigit():
                    x = float(x)

                else:
                    x = x.strip()

            else:
                x = x.strip()

            data.append(x)

        if not check:
            return data,None

        checksum2 = self.xor(string)

        if checksum2 == checksum1:
            return data,True

        else:
            return data,False

    # xor of string
    def xor(self,s):

        check = 0

        for c in s:
            check ^= ord(c)

        return ('0'+hex(check)[2:])[-2:].upper()


# old

### NMEA: $xxVTG,cogt,T,cogm,M,knots,N,kph,K,posMode*cs<CR><LF>
##elif name == 'VTG':
##    if len(line) == 10:
##        nada,tru,nada,mag,nada,knots,nada,kph,nada,nada = line[:10]
##        if tru.strip():
##            data[3] = float(tru)
##        else:
##            data[3] = None
##        if mag.strip():
##            data[4] = float(mag)
##        else:
##            data[4] = None
##        if kph.strip():
##            kph = float(kph)
##            data[5] = kph
##            data[6] = kph/1.609344
##        else:
##            data[5] = None
##            data[6] = None
##    print('VGT:',[line])

### NMEA: $xxZDA,hhmmss.ss,day,month,year,ltzh,ltzn*cs<CR><LF>
##elif name == 'ZDA':
##    if len(line) == 7:
##        hms = line[1]
##        if hms and hms[:6].isdigit():
##            data[0] = (int(hms[:2]) + self.timezone + 24 ) % 24
##            data[1] = int(hms[2:4])
##            data[2] = int(hms[4:6])

