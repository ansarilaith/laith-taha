#-----------------------
# imports
#-----------------------

from micropython import const

#-----------------------
# funboard variables class
#-----------------------

class BOARD:

    BOARD_NAME = 'FUNBOARD-V1'
    BOARD_DATE = '2021-01-06'

    # sdcard ref: https://docs.micropython.org/en/latest/library/machine.SDCard.html
    SDCARD_SLOT   = const( 3) #
    PIN_SD_CS     = const(27) # SDCard non-standard 
    PIN_SD_SCL    = const(14) # SDCard Slot 3
    PIN_SD_MOSI   = const(13) # SDCard Slot 3
    PIN_SD_MISO   = const(12) # SDCard Slot 3
    
    PIN_MANRST    = const(15) #  --> RESET
    PIN_LED       = const(32) # Blue LED
    PIN_PIXELS    = const( 4) # 8 Micro Pixels
    PIN_BUZZER    = const( 2) # Buzzer
    PIN_PROG      = const( 0) # PROG Button
    PIN_UART1_TX  = const(17) # UART
    PIN_UART1_RX  = const(16) # UART
    PIN_SPI2_CS   = const( 5) # SPI-2
    PIN_SPI2_SCL  = const(18) # SPI-2
    PIN_SPI2_MISO = const(19) # SPI-2
    PIN_SPI2_MOSI = const(23) # SPI-2
    PIN_I2C1_DATA = const(26) # I2C-1
    PIN_I2C1_CLK  = const(25) # I2C-1

    @property
    def info(self):
        print('{} {}'.format(self.BOARD_NAME,self.BOARD_DATE))

    @property
    def help(self):
        print('''{} Extras:
    funboard:
        funboard.info
        funboard.help
        dir(funboard) # lists a bunch of pins
    esp32 values:
        esp32.reset # hard reset
        esp32.temp
        esp32.tempf
        esp32.hall
        esp32.memory
        esp32.flash
    beeper-buzzer:
        beeper.beep(frequency,seconds,vol%)
        beeper.beepn(count,frequency,seconds,vol%)
        beeper.beep2(freq1,freq2,seconds,vol%):
        beeper.play(notestring):
    blue led:
        led.on()
        led.off()
        led.blink(count)
    micro pixels:
        set: pixels.brightness = 32 # 0-255, set global
        pixels.off() # all off
        pixels.kill() # makes gpio pin an imput
        pixels.setp(pixel,color,brightness) # set a pixel 0-7
        pixels.set_brightness(32) # set global, adjust current
        pixels.sweep(color,brightness) # like KITT from Knight Rider
    sd card:
        sdcard.mount() # runs on boot
        sdcard.unmount()
        sdcard.sdpath()
        sd.format()
    wifi:
        set: essid = "my_essid"
        set: password = "my_password"
        wifi.scan()
        wifi.connect(essid,password) # or use set values
        wifi.disconnect()
    real time clock:
        rtc.ntp_set() # after wifi connect
        rtc.set(datetime_tuple) # manual set
        rtc.get()
        rtc.linux_epoch()
        rtc.dtstamp()
    eziot:
        set: eziot.api_key = "my_account_key"
        set: eziot.api_secret = "my_account_secret"
        set: eziot.api_version = 1.0
        eziot.stats()
        eziot.post_data(group,device,data1,data2,data3,data4)
        eziot.get_data(count,after,group,device)
        eziot.delete_data(rowids,before,xall)
        eziot.watch(startrows,update,group,device)
    system tools:
        st.tree() # print directory tree structure
            '''.format(self.BOARD_NAME))

#-----------------------
# end
#-----------------------
