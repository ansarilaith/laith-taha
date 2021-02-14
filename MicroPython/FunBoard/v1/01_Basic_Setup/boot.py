#-----------------------
# notify
#-----------------------

print('RUN: boot.py')

#-----------------------
# board setup
#-----------------------

# add library to path
import sys
if '/lib' not in sys.path:
    sys.path.append('/lib')

# basic setup of board devices
import setup_funboard_v1 as _board

# make board devices available everywhere
# adds devices to highest-level namespace
import builtins

builtins.esp32  = _board.esp32  # class
builtins.led    = _board.led    # class
builtins.beeper = _board.beeper # class
builtins.sdcard = _board.sdcard # class

#-----------------------
# wlan object setup
#-----------------------

#from system_networks import WLAN
#builtins.wlan = WLAN()

import system_rtc
builtins.rtc = system_rtc.RTCTOOLS()

#-----------------------
# system tools setup
#-----------------------

import system_tools as st
builtins.st = st

#-----------------------
# user sys setup/cleanup
#-----------------------

del builtins

st.memp()

#-----------------------
# end
#-----------------------
