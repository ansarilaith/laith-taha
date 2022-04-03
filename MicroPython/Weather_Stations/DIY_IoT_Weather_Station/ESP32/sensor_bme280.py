#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: sensor_bme280.py')

# this is set up for weather mode
# call force(), then call get_data()

#-----------------------
# imports
#-----------------------

import time
from ustruct import unpack

#-----------------------
# bme280 via I2C
#-----------------------

class BME280:
    
    # self.get_data() == T,P,H
    # T = temperature celcius
    # P = pressure pascals
    # H = humidity percent relative
    # see additional functions

    #-----------------------
    # I2C setup
    #-----------------------

    # init requires an i2c bus
    # connect SDO to GND = address 118 0x76 (default)
    # connect SDO to VDD = address 119 0x77 (same as BMP)
    address = 0x76

    #-----------------------
    # sensor setup
    #-----------------------

    # --------------------------
    # register 0xF2 = ctrl_hum = humidity control
    #      osrs_h     xxxxx001 = humidity oversampling = 1x (typical, recommended for weather)
    ctrl_hum      = 0b00000001
    # changes take effect after writing to register 0xF4

    # --------------------------
    # register 0xF4 = ctrl_meas = temp pressure control
    #       osrs_t     001xxxxx = temperature oversampling = 1x (typical, recommended for weather)
    #       osrs_p     xxx001xx = pressure oversampling = 1x (typical, recommended for weather)
    #       osrs_p     xxx011xx = pressure oversampling = 4x (for navigation)
    #         mode     xxxxxx11 = sample mode = normal
    #         mode     xxxxxx01 = sample mode = forced (i.e. wake, read, sleep)
    #         mode     xxxxxx00 = sample mode = sleep (for weather, requires setting forced mode before read)
    #ctrl_meas      = 0b00101111 # for navigation
    ctrl_meas      = 0b00100100 # for weather (requires setting forced mode before read)
    
    # --------------------------
    # register 0xF5 = config = timing filter spi-mode
    #      t_sb     000xxxxx = standby timing = 0.5ms
    #      t_sb     101xxxxx = standby timing = 1 sec (for normal mode)
    #    filter     xxx000xx = filter is off
    #    filter     xxx100xx = filter = 16x
    #  spi3w_en     xxxxxxx0 = 4-wire SPI
    #config      = 0b00010000 # for navigation
    config      = 0b10100000 # for weather

    #-----------------------
    # altitude setup
    #-----------------------

    # altitude is derived from the deviation from zero value
    # the zero value is the average pressure at self.altitude_zero call

    # self.altitude_zero() should be called on init because pressure changes constantly
    # however, pressure should remain a similar value for the duration of a short flight
    altitude_P = None

    # altitude = pressure * meter_per_pascal value
    # https://en.wikipedia.org/wiki/Vertical_pressure_variation
    altitude_MPP = 1 / 11.331 # general deviation 0-1000 meters

    # altitude offset in meters at zero value
    # this is added to the differential altitude
    # set to adjust above-ground values to above-sealevel values
    altitude_O = 0

    #-----------------------
    # general setup
    #-----------------------

    # last get-data time
    lgdt = 0

    #-----------------------
    # general functions
    #-----------------------

    # init
    def __init__(self,bus,address=None,altitude=None,altitude_zero=True):

        # set bus
        self.bus = bus

        # set address
        if address in (118,119):
            self.address = address

        # online check
        for x in (0,1,2):
            if self.ok():
                break
            elif x == 2:
                raise Exception('BME Failure')
            time.sleep_ms(333)

        # reset and config device
        self.reset()

        # set altitude offset
        if altitude != None:
            self.altitude_O = altitude

        # set zero
        if altitude_zero:
            self.altitude_zero(altitude)

        # ready
        print('BME Ready')

    # bus+chip check
    def ok(self):
        try:
            check = self.bus.read(self.address,0xD0,1)
            print('BME CHECK:',check)
            if check == [0x60]:
                print('BME Online')
                return True
        except Exception as e:
            print('BME Offline')
            return False

    # reset
    def reset(self):

        # reset device
        self.bus.write(self.address,0xE0,0xB6)
        time.sleep_ms(100)
        
        # set configuration (see variables above)

        # write-check loop
        error = False
        for x in range(3):           

            # write
            self.bus.write(self.address,0xF2,[self.ctrl_hum])
            self.bus.write(self.address,0xF4,[self.ctrl_meas])
            self.bus.write(self.address,0xF5,[self.config])

            # check
            block = self.bus.read(self.address,0xF2,4)
            block.pop(1)
            if block == [self.ctrl_hum,self.ctrl_meas,self.config]:
                if error:
                    print('BME Config Fixed')
                error = False
                break

            print('BME Config Error')
            error = True
            time.sleep_ms(100)

        if error:
            raise(Exception('Unable for set BME config.'))

        # load calibration data from device
        # register 0x88 + 26 = calibration data
        # register 0xE1 +  7 = calibration data (humidity)

        # read part 1 (26 values, starting at 0x88)
        data1 = self.bus.read(self.address,0x88,26,raw=True)

        # unpack part 1
        self.dig_T1,self.dig_T2,self.dig_T3, \
        self.dig_P1,self.dig_P2,self.dig_P3, \
        self.dig_P4,self.dig_P5,self.dig_P6, \
        self.dig_P7,self.dig_P8,self.dig_P9, \
        junkbyte,self.dig_H1= unpack('<HhhHhhhhhhhhBB',data1)

        # read part 2 (7 values, starting at 0xE1)
        data2 = self.bus.read(self.address,0xE1,7,raw=True)

        # unpack part2
        self.dig_H2,self.dig_H3, \
        e4_sign,byte5,e6_sign,   \
        self.dig_H6 = unpack('<hBbBbB',data2)
        self.dig_H4 = (e4_sign << 4) | (byte5 & 0xF)
        self.dig_H5 = (e6_sign << 4) | (byte5 >> 4)

    # force a conversion (if in sleep mode)
    def force(self,wait=1333):
        # max conversion time is 1333 ms
        for x in range(3):
            try:
                # force mode = xxxxxx01, so or default value with 1
                self.bus.write(self.address,0xF4,[self.ctrl_meas|1])
                time.sleep_ms(wait)
                return True
            except:
                time.sleep_ms(10)
        return False          

    # read and convert data (T,P,H)
    def get_data(self):

        # return values
        T,P,H = None,None,None

        # raw data (8 bytes starting at 0xF7)        
        data = self.bus.read(self.address,0xF7,8)
        raw_press = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 4
        raw_temp  = ((data[3] << 16) | (data[4] << 8) | data[5]) >> 4
        raw_hum   =  (data[6] <<  8) |  data[7]

        # temperature celcius (needed first)
        var1 = ((raw_temp >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = (((((raw_temp >> 4) - self.dig_T1) *
                  ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        T = ((t_fine * 5 + 128) >> 8)/100

        # pressure pascals
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) << 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            P = 0
        else:
            P = 1048576 - raw_press
            P = (((P << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (P >> 13) * (P >> 13)) >> 25
            var2 = (self.dig_P8 * P) >> 19
            P = ((P + var1 + var2) >> 8) + (self.dig_P7 << 4)
        P /= 256

        # humidity percent relative
        H = t_fine - 76800
        H = (((((raw_hum << 14) - (self.dig_H4 << 20) -
                (self.dig_H5 * H)) + 16384)
              >> 15) * (((((((H * self.dig_H6) >> 10) *
                            (((H * self.dig_H3) >> 11) + 32768)) >> 10) +
                          2097152) * self.dig_H2 + 8192) >> 14))
        H -= ((((H >> 15) * (H >> 15)) >> 7) * self.dig_H1) >> 4
        H = 0 if H < 0 else H
        H = 419430400 if H > 419430400 else H
        H >>= 12
        H /= 1024

        # done
        self.lgdt = time.ticks_us()
        return T,P,H

    #-----------------------
    # adjustment functions
    #-----------------------

    # pascals adjusted to sea level
    def P2sea(self,P,T,elevation=None):

        # use default altitude if elevation not given
        elevation = elevation or self.altitude_O

        # sea level adjust formula
        return P * ( 1 - ( (0.0065*elevation) / (T + 0.0065*elevation + 273.15) ) )**-5.257

    # pascals to inches Hg adjusted to sea level
    def P2inches(self,P,T,elevation=None):
        return self.P2sea(P,T,elevation)/3386.3887

    # pascals to millibars adjusted to sea level
    def P2millibars(self,P,T,elevation=None):
        return self.P2sea(P,T,elevation)/100

    # celcius to fahrenheit
    def C2F(self,C):
        return C*1.8 + 32

    # weather in C and millibars
    def weather(self,elevation=None):
        T,P,H = self.get_data()
        return T,self.P2millibars(P,T,elevation),H

    # weather in F and inHg
    def weather_us(self,elevation=None):
        T,P,H = self.get_data()
        return self.C2F(T),self.P2inches(P,T,elevation),H

    #-----------------------
    # altitude functions
    #-----------------------

    # zero (meters)
    def altitude_zero(self,altitude=None):

        # mean pressure
        samples = 100
        pause = 5
        P = 0
        for x in range(samples):
            P += self.get_data()[1]
            time.sleep_ms(pause)
        self.altitude_P = P/samples

        # set altitude offset
        if altitude != None:
            self.altitude_O = altitude

        # ready
        print('BME ALT ZERO: {} pascals, {} meters'.format(self.altitude_P,self.altitude_O))

    # altitude (meters)
    def altitude(self):
        # remember higher altitude == lower pressure
        return self.altitude_O + self.altitude_MPP*(self.altitude_P-self.get_data()[1])

    # altitude (meters) plus all other values, i.e. A,T,P,H
    def altitude_plus(self):
        T,P,H = self.get_data()
        return self.altitude_O + self.altitude_MPP*(self.altitude_P-P),T,P,H

#-----------------------
# end
#-----------------------
