#-----------------------
# funboard setup
#-----------------------

# encapsulating function
def setup():

    #-----------------------
    # imports
    #-----------------------

    import time
    import builtins
    
    #-----------------------
    # board variables
    #-----------------------

    from lib.funboard.board import BOARD
    builtins.funboard = BOARD()
    del BOARD

    #-----------------------
    # esp32 hardware
    #-----------------------

    from lib.funboard.esp32 import ESP32
    builtins.esp32 = ESP32(funboard.PIN_MANRST)
    del ESP32

    #-----------------------
    # hardware reset option
    #-----------------------

    from machine import reset_cause
    reset_why = reset_cause()
    print('LAST RESET:',{
        # machine.PWRON_RESET     = 1
        # machine.HARD_RESET      = 2
        # machine.WDT_RESET       = 3
        # machine.DEEPSLEEP_RESET = 4
        # machine.SOFT_RESET      = 5
        1: 'POWERON',
        2: 'HARDWARE',
        3: 'WATCHDOG',
        4: 'DEEPSLEEP',
        5: 'SOFTWARE'}.get(reset_cause,'UNKNOWN'))
    del reset_cause

    # software resets DO NOT clear peripherals
    # machine.reset() and WDT don't do full resets either
    if reset_why >= 3:
        esp32.reset
    del reset_why

    #-----------------------
    # led
    #-----------------------

    from lib.funboard.leds import LED
    builtins.led = LED(funboard.PIN_LED)
    del LED
    led.on()

    #-----------------------
    # beeper
    #-----------------------

    from lib.funboard.beeper import BEEP
    builtins.beeper = BEEP(funboard.PIN_BUZZER)
    del BEEP
    beeper.play(beeper.jingle_notes)

    #-----------------------
    # micro pixels
    #-----------------------

    from lib.funboard.leds import PIXELS
    builtins.pixels = PIXELS(funboard.PIN_PIXELS,8)
    del PIXELS
    pixels.sweep(['red','blue','green'][time.time()%3])

    #-----------------------
    # sdcard
    #-----------------------

    from lib.funboard.sdcard import SDCARD
    builtins.sdcard = SDCARD(slot=funboard.SDCARD_SLOT,
                             cs=funboard.PIN_SD_CS,
                             sck=funboard.PIN_SD_SCL,
                             mosi=funboard.PIN_SD_MOSI,
                             miso=funboard.PIN_SD_MISO)
    del SDCARD
    sdcard.mount()

    #-----------------------
    # wifi tools
    #-----------------------

    from lib.funboard.wifi import WIFI
    builtins.wifi = WIFI()
    del WIFI
    
    #-----------------------
    # rtc
    #-----------------------

    from lib.funboard.rtc import RTCTOOLS
    builtins.rtc = RTCTOOLS()
    del RTCTOOLS

    #-----------------------
    # eziot
    #-----------------------

    import lib.funboard.eziot as ez
    builtins.eziot = ez

    #-----------------------
    # system tools
    #-----------------------

    import lib.funboard.st as st
    builtins.st = st
    
    #-----------------------
    # clean up
    #-----------------------

    del builtins
    st.memp()

    #-----------------------
    # done
    #-----------------------

    beeper.play(beeper.jingle2_notes)
    led.off()

    funboard.info
    print('For help try "funboard.help".')
    print('Ready to Go!')

# run
setup()

#-----------------------
# end
#-----------------------
