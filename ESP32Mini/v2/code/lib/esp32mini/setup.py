#-----------------------
# esp32mini setup
#-----------------------

# encapsulating function
def setup():

    #-----------------------
    # imports
    #-----------------------

    import os
    import time
    import builtins
    
    #-----------------------
    # board variables
    #-----------------------

    from lib.esp32mini.board_v2 import BOARD
    builtins.esp32mini = BOARD()
    del BOARD

    #-----------------------
    # esp32 hardware
    #-----------------------

    from lib.esp32mini.esp32 import ESP32
    builtins.esp32 = ESP32(esp32mini.PIN_MANRST)
    del ESP32

    #builtins.reboot = esp32.reset
    #builtins.minihelp = esp32mini.help

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
        5: 'SOFTWARE'}.get(reset_why,'UNKNOWN: {}'.format(reset_why)))
    del reset_cause

    # software resets DO NOT clear peripherals
    # machine.reset() and WDT don't do full resets either
    if reset_why not in (1,2,4):
        esp32.reset
    del reset_why

    #-----------------------
    # led
    #-----------------------

    from lib.esp32mini.leds import LED
    builtins.led = LED(esp32mini.PIN_LED)
    del LED
    led.on()

    #-----------------------
    # wifi tools
    #-----------------------

    from lib.esp32mini.wifi import WIFI
    builtins.wifi = WIFI()
    del WIFI
    
    #-----------------------
    # rtc
    #-----------------------

    from lib.esp32mini.rtc import RTCTOOLS
    builtins.rtc = RTCTOOLS()
    del RTCTOOLS

    #-----------------------
    # eziot
    #-----------------------

    import lib.esp32mini.eziot as ez
    builtins.eziot = ez

    #-----------------------
    # system tools
    #-----------------------

    import lib.esp32mini.st as st
    builtins.st = st
    
    #-----------------------
    # clean up
    #-----------------------

    del builtins
    st.memp()

    #-----------------------
    # done
    #-----------------------
    print(esp32mini.ASCIIART)
    led.off()
    esp32mini.info
    print('ESP32 Mini is ready to go!')
    print('For help try "esp32mini.help".')
    print('\n')

# run
setup()

#-----------------------
# end
#-----------------------
