#----------------------- 
# notify
#-----------------------

print('RUN: main.py') 

#----------------------- 
# safety catch
#-----------------------

import time
for x in range(100):
    time.sleep_ms(10)

#-----------------------
# notes
#-----------------------

#-----------------------
# configuration values
#-----------------------

#-----------------------
# imports
#-----------------------





#-----------------------
# run
#-----------------------

def run():

    # build i2c port
    from ssd1306 import SSD1306_I2C
    global p
    p = SSD1306_I2C()
    p.scl = 25
    p.sda = 26
    p.port = 1
    p.freq = 100000 # low rate to start (try x4 for max)
    p.addr = None

    p.port_open()

    

#-----------------------
# run on start
#-----------------------

if __name__ == '__main__':
    run()

#-----------------------
# end
#-----------------------
