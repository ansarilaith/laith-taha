# notify
print('RUN: main.py')

import os,time
from machine import Pin, SPI

import ftree
import ssd1306

############################
# oled init
############################

oled = ssd1306.SSD1306_128X64_GRID()
oled.port = 1
oled.baudrate *= 8
oled.port_open(test=False)
oled.contrast(255)
oled.r180()

oled.randomflash(1028,0)
oled.frame_clear()

############################
# intro
############################

time.sleep(0.25)

oled.frame_clear()
oled.place_text('Random',64,32-16,scale=1,center=True,middle=True,value=1)
oled.place_text('Fractal',64,32,scale=2,center=True,middle=True,value=1)
oled.place_text('Trees',64,32+16,scale=1,center=True,middle=True,value=1)
oled.frame_show()
oled.fadeinout(pause=0.001)

time.sleep(0.25)

oled.frame_clear()
oled.place_text('ESP32',64,32,scale=2,center=True,middle=True,value=1)
oled.frame_show()
oled.fadeinout(pause=0.001)

time.sleep(0.25)

oled.frame_clear()
oled.place_text('OLED',64,32-7,scale=2,center=True,middle=True,value=1)
oled.place_text('128 x 64 0.96 in',64,32+8,scale=1,center=True,middle=True,value=1)
oled.frame_show()
oled.fadeinout(pause=0.001)

time.sleep(1)

############################
# fractal trees
############################

ft = ftree.FTree()
while 1:

    oled.frame_clear()
    oled.contrast(255)

    for x,y in ft.rtree(64,0):
        oled.bitset(x,64-y)
        oled.frame_show()
        time.sleep(0.01)

    time.sleep(1)
    oled.fadeout(pause=0.001)
    time.sleep(0.25)

############################
# done
############################

oled.fadeout()
oled.blank()






















