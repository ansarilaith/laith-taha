#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: bus_i2c.py')

#-----------------------
# imports
#-----------------------

from machine import Pin, I2C

#-----------------------
# i2c bus
#-----------------------

class I2CBUS:

    def __init__(self,scl=25,sda=26,freq=400000):
        self.bus = I2C(1,scl=Pin(scl),sda=Pin(sda),freq=freq)

    def kill(self):
        try:
            # most boards don't have this
            self.bus.deinit()
        except:
            pass

    def reset(self):
        self.kill()
        self.__init__()

    def scan(self):
        addrs = self.bus.scan()
        for x in addrs:
            print('I2C ADDR:',x,'{:0>8}'.format(bin(x)[2:]),'{:0>2}'.format(hex(x)[2:]))
        return addrs

    # this requires a buffer
    def write(self,address,memory,buffer):
        self.bus.writeto_mem(address,memory,bytearray(buffer))

    # default return is a list of intergers, raw is a bytearray
    def read(self,address,memory,nbytes,raw=False):
        if raw:
            return self.bus.readfrom_mem(address,memory,nbytes)
        else:
            return list(self.bus.readfrom_mem(address,memory,nbytes))

    # bit modify given register
    def bitmod(self,address,memory,mask,value):

        # get value
        (current,) = self.read(address,memory,1)

        # modify
        current |= (value&mask)

        # write
        self.write(address,memory,[current])

        # check
        #print('BITMOD:',address,memory,[bin(current)],bin(self.read(address,memory,1)[0]))
        return self.read(address,memory,1) == [current]
       
#-----------------------
# end
#-----------------------
