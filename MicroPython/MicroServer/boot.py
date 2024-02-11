#-----------------------
# notify
#-----------------------

print('RUN: boot.py')

#-----------------------
# hard reset check
#-----------------------

# reset pin
_MANRST = 15

# get reset cause
# machine.PWRON_RESET     = 1
# machine.HARD_RESET      = 2
# machine.WDT_RESET       = 3
# machine.DEEPSLEEP_RESET = 4
# machine.SOFT_RESET      = 5
from machine import reset_cause
reset_cause = reset_cause()
print('LAST RESET:',{1:'POWERON',2:'HARDWARE',3:'WATCHDOG',4:'DEEPSLEEP',5:'SOFTWARE'}.get(reset_cause,'UNKNOWN'))

# no soft resets
if reset_cause == 5:
    from machine import Pin
    Pin(_MANRST,Pin.OUT,value=0)

# clean up
del _MANRST,reset_cause

#-----------------------
# construct builtins
#-----------------------

import builtins

# ---- file manager tools ----

# for testing leave all of these
# for production comment out the unused
import ostools as ot
builtins.listdir = ot.listdir
builtins.stat    = ot.stat
builtins.fsize   = ot.fsize
builtins.isfile  = ot.isfile
builtins.fmatch  = ot.fmatch
builtins.remove  = ot.remove
builtins.abspath = ot.abspath
builtins.pwd     = ot.pwd
builtins.cwd     = ot.cwd
builtins.isdir   = ot.isdir
builtins.exists  = ot.exists
builtins.touch   = ot.touch
builtins.mkdir   = ot.mkdir
builtins.tree    = ot.tree
builtins.cat     = ot.cat
del ot

# ---- board tools ----

##from some_board_00 import BOARD
##builtins.board = BOARD()
##del BOARD

# ---- clean up ----

del builtins

#-----------------------
# final cleanup
#-----------------------

from gc import collect
collect()

del collect

#-----------------------
# end
#-----------------------

