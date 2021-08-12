# The FunBoard V2

The Funboard is designed to be a low-cost solution for **learning to program** and experimenting with **embedded devices** and the **Internet-of-Things** (IoT).
The board and its open-source software package provides everything you need to quickly get started programming using Python and MicroPython, some of the most popular and practical programming languages in use today.
You can easily develop your basic programming skills and knowledge base (i.e. variables, functions, loops, etc.) using the on-board LEDs, MicroPixels and buzzer.
And when you are ready, you can move on to advance topics and projects like IoT devices and network programming, all using the built-in IO pins, microSD card, and WiFi capability.
Whatever your programming level, a creative mind will never run out of projects for the FunBoard.
Although I've been programming for 20 years, I use FunBoards everyday for developing and experimenting.

Here are some of the FunBoard's features:

- USB powered
- USB interface (serial TTY)
- ESP32 processor
- WiFi
- two switches (reset and programmable)
- microSD card slot
- 13 extra IO pins
- SPI, I2C, UART
- programmable LED
- buzzer
- 8 programmable MicroPixels
- MicroPython
- full support software for peripherals
- ongoing support and tutorials

<table><tr>
<td width="50%"><img alt="front" src="/FunBoard/v2/images/v2_front.jpg"/></td>
<td width="50%"><img alt="back"  src="/FunBoard/v2/images/v2_back.jpg" /></td>
</tr></table>

# In This Repository

- **applications** - this contains application code from YouTube videos which use the FunBoard V2
- **images** - this contains the last MicroPython image tested using FunBoard V2 code
- **code** - this contains the code you need to run the FunBoard V2 (should be pre-loaded)
- **bin** - binary images (MicroPython + support software) you can load onto your FunBoard
- **images** - pretty pictures of FunBoards 

# Documentation
## Content Links

### Local Links:
- [Safety Precautions](#safety)
- [Peripherals](#peripherals) - GPIO pins, LEDs, Buzzer, etc.
- [Connecting Via USB3c](#connecting)
- [FunBoard Built-In Functions](#built-in-functions) - everything fun on the FunBoard
- [How to Load Code, Scripts, and Files](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/code)
- [How to Load a MicroPython Image](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/bin)

### External Links
- [MicroPython General Docs](http://docs.micropython.org/en/latest/)
- [MicroPython ESP32 Quick Reference](http://docs.micropython.org/en/latest/esp32/quickref.html)
- [ClaytonDarwin on YouTube](https://www.youtube.com/claytondarwin)
- [EZIoT.link](https://eziot.link)
- [Clayton's Server on a FunBoard](http://eziot.link/dns/clayton)

### Where to Buy a FunBoard
- [The PCBWay Store](https://www.pcbway.com/project/gifts_detail/The_FunBoard_V2.html) - use this if you are outside the U.S.
- [Clayton's PCB Shop](https://cpcb.shop/) - if you are in the U.S. this might be cheaper.

### Videos

- [A FunBoard Server](https://www.youtube.com/watch?v=SktBsA3xvDI)
- [Quick Preview: FunBoard V2](https://www.youtube.com/watch?v=H8-ObIHnE7s)
- [UnBoxing the FunBoard V1](https://www.youtube.com/watch?v=AA9ynxTzcaQ)
- More coming soon!

## Safety

These precautions should be followed to avoid permanently damaging your FunBoard:
1. **USB-Power Only** - the FunBoard should be powered **ONLY** via a USBc connector attached to a regulated 5V 500+mA power supply.
1. **3V GPIO Only** - the GPIO pins **MUST NOT** be connected to a voltage source greater than 3v.
1. **25mA Max on GPIO Pins** - the current per GPIO pin **MUST BE LIMITED** to 25mA.
1. **100mA Max on Source Pins** - the current per source pins (+5V, 3.3V) **MUST BE LIMITED** to 100mA.
1. **No Shorts** - be careful to not allow an unintended short (direct connection) between any of the GPIO pins. 
Be careful not to accidentally connect pins with metal tools, wires, liquids, or any other conductive material.
1. **Always Clean and Dry** - the FunBoard is not water resistant. Always keep it clean and dry in a protective case. 

## FunBoard Peripherals

### USB Connector

The **USB 3 Type C** connector on the FunBoard has two functions.
First, it provides power to the FunBoard. 
It should always be connected to a regulated 5V source that can provide at least 500mA current. 
This is the only recommended method for powering your FunBoard.

Second, the USB connecor creates a serial connection via a **Silicon Labs CP210x USB to UART Bridge IC** that you can use to interact with the ESP32 (see [Connecting](#connecting) below). 
If you are using Linux or OSX, the required drivers should be included in the Kernel (or you definitely need an update). 
For Windows you will need to install the driver. 
You can get it here: [Silicon Labs Drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

### Switches

There are two push-button switches on the funboard:

- RESET - pushing this will cause a hard reset of the ESP32. 
You can accomplish the same thing using the `esp32.reset` function (see [esp32](#esp32) below).

- PROG - holding this button down while pushing the RESET button to put the ESP32 into program mode (see [Images](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/bin) for more information).
Any other time, this button is connected to GPIO 0 and can be used as a user input.

### MicroSD Card Slot

The MicroSD card slot has been tested with SD cards from 4GB to 16GB.
Most seem to function well, but if you are having issues, try a different card.

You can mount and access the SD card using the built-in `sdcard.xxx` functions (see [sdcard](#sdcard) below). 

### LEDs

There are two LEDs in the top-left corner of the FunBoard.
The green one is on whenever power is connected to the FunBoard.
You can control the blue one using the built-in `led.xxx` functions (see [led](#led) below).

### MicroPixels

There are 8 MicroPixels along the lower edge of the FunBoard.
They are labeled 7-0, which it the normal way to label bits (MSB order).
You can control the MicroPixels directly (set their color and brightness) using the built-in `pixels.xxx` functions (see [pixels](#pixels) below).
The MicroPixels can also be connected to the `beeper.play()` function by setting `dopixels=True`. This will cause the pixels to light up according to the note and octave being played.

### Buzzer

The buzzer on the FunBoard can be used as in indicator, or to play simple musical tunes. 
There are a lot of built-in functions that will help you get started. 
See the `beeper.xxx` functions below (see [beeper](#beeper)). 

### GPIO Pins

- 16 - GPIO - UART RX (input) 
- 17 - GPIO - UART TX (output)
- 5 - GPIO - SPI-2 CS (chip select) -
- 18 - GPIO - SPI-2 CL (clock) -
- 19 - GPIO - SPI-2 DI (MISO data in) -
- 23 - GPIO - SPI-2 DO (MOSI data out) -
- 25 - GPIO - I2C-1 CL (clock) -
- 26 - GPIO - I2C-1 DA (data) -
- 35 - Input Only - ADC1-7 
- 39 - Input Only - ADC1-3
- +5V - 5V 100mA (max) source for peripheral device
- G - GND - gound pin for peripheral device
- 3.3V - 3.3V 100mA (max) source for peripheral device
- G - GND - gound pin for peripheral device
- G - GND - gound pin for peripheral device
- 21 - GPIO 
- 22 - GPIO  
- 33 - GPIO - ADC1-5
- 34 - Input Only - ADC1-6
- 36 - Input Only - ADC1-0

## Connecting

Here is the basic information you need to get connected to your FunBoard and load your programs. 
Keep in mind that there are other ways to do this. 
Any software designed for an ESP32-plus-MicroPython setup will probably work for the FunBoard, so no harm in trying.

### Serial REPL via the USB Connector

The FunBoard connects to your laptop or desktop using a **USB 3 Type C** cable. When connected, the USB port is converted to TTY serial by a **Silicon Labs CP210x USB to UART Bridge IC**. If you are using Linux or OSX, these drivers should be included in the Kernel (or you definitely need an update). For Windows you will need to install the driver. You can get it here: [Silicon Labs Drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

Here are the basic serial-port specifications:
- 115200 baud
- 8 bits
- No parity bit
- 1 stop bit

Once you connect, you will be attached to the MicroPython REPL (read-evaluate-print-loop). 
This will function just like a Python command-line prompt and allow you to run scripts and see output.

And here are some different methods for connecting to the FunBoard via a serial port:

#### Putty

For the Windows OS, most people use the [Putty](https://www.putty.org/) software.
I will add some instructions soon (once I have had a chance to test it).

#### Picocom

In Linux, you must add your username to the `dialout` group and then **log out** or **reboot**.
```
sudo adduser your_username dialout
```

Install:
```
sudo apt install picocom
```

Connect:
```
picocom -b 115200 /dev/ttyUSB1
```
Be sure to set your port to the correct one.

Disconnect:

Use `ctrl-a crtl-x` to exit picocom and return to the command prompt.

#### Python + PySerial

Ref: [PySerial Docs](https://pythonhosted.org/pyserial/)

Add your username to the `dialout` group and then **log out** or **reboot**.
```
sudo adduser your_username dialout
```

Add the PySerial module from the command line:
```
python3 -m pip install pyserial
```

Basic usage in Python:
```
uart = serial.Serial('/dev/ttyUSB1',115200) # 9600,8,N,1 is default

uart.open()
uart.read(1024)
uart.write(b'some bytes')
uart.close()
```

Or this:
```
uart = serial.Serial()
uart.baudrate = 115200
uart.port = '/dev/ttyUSB1'
uart.timeout = 0

uart.open()
uart.read(1024)
uart.write(b'some bytes')
uart.close()
```

### Loading Programs and Files

Once you have established a connection to the FunBoard you will need to load your own programs and files.
Again, keep in mind that there are different ways to do this (and new software coming out all the time). 
Here are some links to separate pages that show you how I load files and images:

- [How to Load Code, Scripts, and Files](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/code)
- [How to Load a MicroPython Image](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2/bin)

## Built In Functions

The FunBoard comes with software to support all of the attached board peripherals like the MicroSD card, the leds, beeper, etc.
There are also a lot of convenience functions included for common events such as connecting to WiFi, file and directory management, and using the Real-Time-Clock.

Most of the class names are self-explanatory, but be sure to have a look at the obscure ones like **st**, which has lots of handy functions for exploring the file system, and **esp32**, which has some *esp32-specific* functions.

### beeper
This modules controls the onboard **buzzer**. You can set the module default values before calling the functions, or you can provide values when the functions are called.

Here are default values:
- `beeper.freq` - Frequency integer = 2200 
- `beeper.freq2` - Second frequency integer for `beep2` = `beeper.freq*2`
- `beeper.secs` - Beep duration milliseconds = 0.125
- `beeper.duty` - Percent duty cycle for PWM = 25
- `beeper.vol` - Volume percent = 100
- `beeper.wait` - Pause between beeps = `beeper.secs/2'
- `beeper.fcps` - Number of frequency changes per second for `beep2` = 100
- `beeper.root` - Root frequency for `play` = 440
- `beeper.beat` - Beat length for `play` = 0.125

Here are the functions:
- `beeper.beep(freq=None,secs=None,vol=None,duty=None,pixel=None,color=None)` - Beep the buzzer. No values are required (will use defaults). The `pixel` and `color` values can be used to turn on a micropixel while the note is played. Use the micropixel index 7-0 and a color string from `pixels.colors`.
- `beeper.beepn(count=1,wait=None,freq=None,secs=None,vol=None,duty=None,pixel=None,color=None,wait=None)` - Beep the buzzer `n` times. No values are required (will beep once using defaults). Works the same as `beep` except for the `count` and `wait` values.
- `beeper.beep2(freq=None,freq2=None,secs=None,vol=None,duty=None,fcps=100)` - Beep the buzzer, but change from `freq` to `freq2` over `secs` seconds. No values are required (will use defaults).
- `beeper.play(notestring=None,root=None,beat=None,vol=None,duty=None,dopixels=False)` - Play a song (a string of notes). No values are required (will play `beeper.shave_notes`). If `dopixels` is set to `True`, notes will be displayed on the micropixels while they play.

Here is the song-string syntax:
- notestring - Any string of a `note/pause + optional_sharp + octave + beats` sequences.
- note - Any character in "ABCDEFG" or "abcdefg".
- sharp - The pound character "#" makes a note sharp (there are no flats, so use a sharp).
- octave - Any digit 0-9. This designates the octave to use. Note that octaves 0, 1, 2 and 9 may not be playable on the buzzer or audible to adults.
- beats - Any non-negative integer. This is the duration of the note in beats (default is 1). There are no partials, so make your `beeper.beat` length match the smallest partial note.
- pause - Either a "P" or "p" character. Works the same as a note, but does nothing for the given beat.
- caps-spaces-other - Ignored. "d44" == "D44" == "d 4 4" == "d, 4, 4" == "D4-4"
- example - Middle C for 3 beats = 'C43'
- example - A pause for 3 beats = 'P3' or 'P03'

These are built in:
- `beeper.jingle_notes` - Jingle (plays on boot) = 'e5 g5 b5 d6 p d5'
- `beeper.jingle2_notes` - Jingle2 (plays after boot) = 'd7'
- `beeper.shave_notes` - Included song *Shave and a Haircut* = 'c4 p g3 g3 a32 g32 p p b3 p c4'
- `beeper.axelf_notes` - Included song *Axel-F* = 'd44 f43 d42 d41 g42 d42 c42 d44 a43 d42 d41 a#42 a42 f42 d42 a42 d52 d41 c42 c41 a32 e42 d46'

### funboard
FunBoard **Help** and information.
- `funboard.info` - FunBoard version data.
- `funboard.help` - List FunBoard extra modules.
- `funboard.show(module=None)` - List functions for a given module based on the **string** name (i.e. use quotes)

### esp32
Here are a few **ESP32**-related variables.
- `esp32.reset` - Do a hard reset of the ESP32.
- `esp32.temp` - Read the ESP32 die temperature in Celsius. 
- `esp32.tempf` - Read the ESP32 die temperature in Ferinheight.
- `esp32.hall` - Read the ESP32 Hall-Effect sensor.
- `esp32.memory` - Get stats (a dict) for the RAM usage.
- `esp32.flash` - Get stats (a dict) for flash usage.

## eziot
The [EZIoT.link](https://eziot.link/) cloud data API is included. Be sure to check out the docs on the [EZIoT.link](https://eziot.link/) web page.
- `eziot.stats()` - Check your stats.
- `eziot.watch(startrows=10,update=10,group=None,device=None)` - Watch your data update.
- `eziot.post_data(group=None,device=None,data1=None,data2=None,data3=None,data4=None)` - Post some data.
- `eziot.get_data(count=1,after=None,group=None,device=None)` - Get some data.
- `eziot.delete_data(rowids=[],before=None,xall=False)` - Delete some data.
- `eziot.get_dns()` - Get current dynamic DNS setup variables.
- `eziot.set_dns(https=False,port=None,plus=None,dnsid=None)` - Set and start dynamic DNS service.
- `eziot.unset_dns()` - Stop the dunamic DNS service.


### led
Control the **Blue LED**.
- `led.on()` - Turn the blue LED on.
- `led.off()` - Turn the blue LED off.
- `led.blink(count=1,ontime=None,offtime=None)` - Blink the blue LED. You can set the number of blinks using `count=n`. You can also set the `ontime` and `offtime` in milliseconds. Defaults are on for 50ms and off for 250ms.
- `led.pwmx(force=False)` - Turn of pulse-width modulation (see below). You can also use `led.off()`.
- `led.pwm(percent=100)` - Turn on blue LED using pulse-width modulation. This allows you to control brightness. Provide an integer percent from 0 (off) to 100 (full brightness).
- `led.pwm2(start=0,end=100,pause=10)` - Progressive change of blue LED from `start` percent to `end` percent, pause `pause` milliseconds between steps (sets how long the transition tales). This allow a fade in, fade out option.

### pixels
Control the **MicroPixels** RGB smart LEDs.

The micropixels are controlled by providing a pixel address, a color tuple of RGB, and a brightness. The `pixels` class has a default brightness (32 out of 255), and it provides a dictionary of basic colors which can be referenced using a name string instead of a tuple. Values for both brightness and RGB levels are integers from **0** to **255**. Pixels are addressed from 7 to 0, from left to right (like bits in MSB order).

- `pixels.off()` - Turn off all pixels.
- `pixels.set_brightness(brightness=0)` - Set the default brightness value 0 to 255.
- `pixels.clist()` - Print the included basic colors to screen.
- `pixels.colors` - A dictionary of basic color names and color values.
- `pixels.get_color(color,brightness=None)` - Get an RGB tuple for the given color tuple/name at the given or default brightness. Defaults to `'white'` at the default brightness.
- `pixels.setp(pixel,color,brightness=None,write=True)` - Set the pixel at address `pixel` to the given `color` using a given `brightness` (or the default). If `write` is False, set the value in memory but don't update the pixels. Otherwise, update the pixels.
- `pixels.sweep(color=None,brightness=None,ontime=25,offtime=5)` - Do an up-and-back sweep of the pixels using the given values. No values are required.

### rtc
**Real-Time Clock** functions. 
- `rtc.ntp_set()` - Set local time using network time server. Requires an established WiFi connection. May time out without setting (not sure why at this point). If it fails, let the connection stabilize and try again.
- `rtc.set(datetime_tuple)` - Set local time manually. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.get()` - Get local time as a tuple of numbers. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.linux_epoch` - Get the Linux epoch time integer (seconds since Jan 1 1970). Differs from ESP32 time stamp.
- `rtc.dtstamp` - Get local time as a string: `2021-05-27 18:42:35 UTC`

### sdcard
**Micro SD Card** tools.
- `sdcard.sdpath(path=None)` - Show the current path string to the SD card **OR** convert the given path to a path on the SD card.
- `sdcard.mount()` - Mount an SD card that has been loaded after boot. You may need to call `sdcard.unmount()` before mounting if the card was removed improperly.
- `sdcard.unmount()` - Unmount any SD card (before removing it).
- `sdcard.format()` - **DELETE ALL DATA** and the SD card and format it.

### st
The **System Tools** module provides a range of convenience functions for working with files, directories, and memory.
- `st.abspath(fd=None)` - Try to build a full, correct path string from the given path string.
- `st.isfile(f)` - Test if string `f` is a file. Return True|False.
- `st.isdir(d)` - Test if string `d` is a directory. Return True|False.
- `st.exists(fd)` - Test if path string `fd` exists. Return True|False.
- `st.tree(d=None,i=0)` - Print a tree structure of the given or current path string. No values are required.
- `st.mkdir(d)` - Try to make a directory at the given path string.
- `st.remove(f)` - Try to remove a file `f`.
- `st.rmdir(d)` - Try to recursively remove directory `d`.  
- `st.pf(f)` - Try to print the content (test) of file path `f`.
- `st.printfile(f)` - Same as `st.pf`.
- `st.pp(obj,depth=0,indentline=True,newline=True,end='\n')`
- `st.ps(obj,depth=0,indentline=True,newline=True,jsonify=False)`
- `st.reload(module)` - Delete and reload a module based on the **string** name (i.e. use quotes). 
- `st.du(d=None,h='MB',show=True,rt=False)` - Show the disk (file storage space) usage.
- `st.memp(show=True,collect=True,rt=False)` - Show the current memory usage after a garbage collect.

### wifi

WiFi requires a **2.4 GHz** access point.

**WiFi Connect** functions.
- `wifi.scan()` - Print available wifi networks to the screen.
- `wifi.connect(essid=None,password=None,timeout=15)` - Connect to a wifi access point with ID `essid` using the given `password` or None if the network is open.
- `wifi.ip(full=False)` - Return current assigned IP address. If `full` return a 4-tuple `(ip, subnet, gateway, dns)`.
- `wifi.disconnect(timeout=15)` - Disconnect from wifi.

 
