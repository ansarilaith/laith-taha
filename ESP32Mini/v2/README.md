# The ESP32Mini V2

The ESP32Mini is designed to be a low-cost, minimal solution for experimenting with **embedded devices** and the **Internet-of-Things** (IoT).
The ESP32Mini is intended for intermediate to advanced users who are looking for a functional ESP32 development board with minimal size. 

<table>
<tr>
<td width="25%"><img alt="front" src="/ESP32Mini/v2/images/esp32miniv1_front.jpg"/></td>
<td width="25%"><img alt="front" src="/ESP32Mini/v2/images/esp32miniv2_front.jpg"/></td>
<td width="25%"><img alt="front" src="/ESP32Mini/v2/images/esp32miniv2b_back.jpg"/></td>
<td width="25%"><img alt="front" src="/ESP32Mini/v2/images/esp32miniv2_back.jpg"/></td>
</tr>
</tr>
</table>

Here are some of the ESP32Mini's features:

- ESP32-WROOM-32E (latest ESP32 core)
- 25.4mm x 31mm layout (2.54mm x 22.86mm pin spacing)
- breadboard compatible
- 16 usable GPIO pins
- 5v or 3.3v powered
- 5v to 3.3v 600ma regulator
- green power LED
- blue LED on GPIO2 (programmable)
- hard reset via GPIO4 (programmable)
- reset button
- program button (programmable) on GPIO0
- program/connect via UART0
- flat back for easy mounting
- MicroPython OS image with added functions
- full support software for peripherals
- ongoing support and tutorials

And the ESP32-WROOM-32E in general:

- latest ESP32 core
- WiFi, BLE (Bluetooth Low Energy), SPI, I2C, UART
- ADC, DAC, PWM on GPIO
- MicroPython, Arduino, Lua, AT, etc support
- built in TEMP, HALL Effect sensors
- 4M flash memory

# In This Repository

- **applications** - this contains application code from YouTube videos which use the ESP32Mini V2
- **images** - this contains the last MicroPython image tested using ESP32Mini V2 code
- **code** - this contains the code you need to run the ESP32Mini V2 (should be pre-loaded)
- **bin** - binary images (MicroPython + support software) you can load onto your ESP32Mini
- **images** - pretty pictures of ESP32Minis 

# Documentation
## Content Links

### Local Links:
- [Safety Precautions](#safety)
- [Peripherals](#peripherals) - GPIO pins, LEDs, etc.
- [Connecting Via UART](#connecting)
- [ESP32Mini Built-In Functions](#built-in-functions)
- [How to Load Code, Scripts, and Files](https://gitlab.com/duder1966/youtube-projects/-/tree/master/ESP32Mini/v2/code)
- [How to Load a MicroPython Image](https://gitlab.com/duder1966/youtube-projects/-/tree/master/ESP32Mini/v2/bin)

### External Links
- [MicroPython General Docs](http://docs.micropython.org/en/latest/)
- [MicroPython ESP32 Quick Reference](http://docs.micropython.org/en/latest/esp32/quickref.html)
- [ClaytonDarwin on YouTube](https://www.youtube.com/claytondarwin)
- [EZIoT.link](https://eziot.link)
- [Clayton's Server on a ESP32Mini](http://eziot.link/dns/clayton)

### Where to Buy a ESP32Mini
- [The PCBWay Store] (coming soon) - use this if you are outside the U.S.
- [Clayton's PCB Shop](https://cpcb.shop/) - if you are in the U.S. this might be cheaper.

### Videos

- [UnBoxing the ESP32Mini V1](https://www.youtube.com/watch?v=TyhTJ6KHVcI)
- [UnBoxing the ESP32Mini V2 (Short)](https://www.youtube.com/watch?v=gXNJLEeIaY0)
- [An ESP32 Server](https://www.youtube.com/watch?v=SktBsA3xvDI)
- [Using Stepper Motors](https://www.youtube.com/watch?v=aVaOmtFGesI)
- More coming soon!

## Safety

<table><tr>
<td><img alt="danger" height="96px" src="/ESP32Mini/v2/images/danger.jpg"/></td>
</tr></table>

These precautions should be followed to avoid permanently damaging your ESP32Mini:
1. **3v Max on the 3v Pin** - as an input this is an unregulated pin. Never exceed 3.3v on this pin.
1. **400mA Max Source on 3v Pin** - if you use the 3v pin as a current source (from the 5v to 3v regulator), do not exceed 400mA. The regulator only supplies 600mA, and the ESP32 can use 200mA while transmitting. Also be careful about overheating if high current is sourced for extended periods.
1. **6v Max on the 5v Pin** - the 5v to 3v regulator can only handle a maximum of 6v input 
1. **25mA Max on GPIO Pins** - the current per GPIO pin **MUST BE LIMITED** to 25mA.
1. **No Shorts** - be careful to not allow an unintended short (direct connection) between any of the GPIO pins. 
Be careful not to accidentally contact/connect pins with metal tools, wires, liquids, or any other conductive material.
1. **Always Clean and Dry** - the ESP32Mini is not water resistant. Always keep it clean and dry in a protective case. 

## ESP32Mini Peripherals

### Switches

There are two push-button switches on the ESP32Mini:

- RESET - pushing this will cause a hard reset of the ESP32. 
You can accomplish the same thing using the `esp32.reset` function (see [esp32](#esp32) below).

- PROG - holding this button down while pushing the RESET button will put the ESP32 into program mode (see [images](https://gitlab.com/duder1966/youtube-projects/-/tree/master/ESP32Mini/v2/bin) for more information).
Any other time, this button is connected to GPIO0 and can be used as a user input.

### LEDs

There are two LEDs in the lower-right of the ESP32Mini.
The green one is on whenever power is connected to the ESP32Mini.
You can control the blue one using the built-in `led.xxx` functions (see [led](#led) below).

### 5v to 3v Regulator

The ESP32Mini has a 5v to 3.3v regulator bridging the 5v and 3v pins. This allows the board to be powered with 5v (on the 5v pin) or 3v (on the 3v pin). The regulator will actually accept up to 6 volts as input to the 5v pin. It can also source up to 400mA at 3.3v from the 3v pin. This will allow you to power some small 3.3v peripheral devices from the 3v pin while powering the ESP32Mini with 5v.

### GPIO Pins

- 33 - GPI_ - input only - ADC1-5
- 32 - GPI_ - input only - ADC1-4
- 27 - GPIO - ADC2_7
- 26 - GPIO - ADC2_9
- 25 - GPIO - ADC2_8
- 14 - GPIO - ADC2_6
- 13 - GPIO - ADC2_4
- 12 - GPIO - ADC2_5
-  G - Ground GND
- 3v - 3.3v power or 3.3v 400mA source with 5v power
- 5v - 5v power
- 15 - GPIO - ADC2_3
- 16 - GPIO - UART2_RX
- 17 - GPIO - UART2_TX
- 18 - GPIO - SCK
- 19 - GPIO - MISO
- 21 - GPIO - SDA
-  3 - RX0 - REPL and programming UART RX (receive/input)
-  1 - TX0 - REPL and programming UART TX (transmit/output)
-  G - Ground GND
- 22 - GPIO - SCL
- 23 - GPIO - MOSI

## Connecting

Here is the basic information you need to get connected to your ESP32Mini and load your programs. 
Keep in mind that there are other ways to do this. 
Any software designed for an ESP32-plus-MicroPython setup will probably work for the ESP32Mini, so no harm in trying.

### Serial REPL via GPIO 16 and 17

Basically, you will need to connect a TTL-level serual UART to GPIO pins 16 and 17.
I recommend a USB-to-TTY_Serial conversion cable. 
There are expensive industrial-grade cables made by FTDI,
and there are cheaper ones that use the Silicon Labs chip.
I tend to use the cheaper ones which can be found on ebay for a few dollars,
but I do have a few FTDI cables too. If you are using Windows, you will need to install the drivers for the cable you are using (Google FTDI or Silicon Labs Windows drivers and get them directly from the company website).

Here are the required pin connections:

- UART TX --> ESP32Mini pin 16 (RX)
- UART RX --> ESP32Mini pin 17 (TX)
- UART Ground --> ESP32Mini GND (2 options)

And you can optionally connect the 5v pin from the UART to the 5v on the ESP32Mini if your cable can supply enough current (usually they can supply 500ma on USB2). Here is a typical USB-to-TTY serial cable:

<table><tr>
<td><img alt="cable" width="75%" src="/ESP32Mini/v2/images/USB_TTY_cable_labeled.jpg"/></td>
</tr></table>

Here are the basic serial-port specifications:
- 115200 baud
- 8 bits
- No parity bit
- 1 stop bit

Once you connect, you will be attached to the MicroPython REPL (read-evaluate-print-loop). 
This will function just like a Python command-line prompt and allow you to run scripts and see output.

And here are some different methods for connecting to the ESP32Mini via a serial port:

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

Once you have established a connection to the ESP32Mini you will need to load your own programs and files.
Again, keep in mind that there are different ways to do this (and new software coming out all the time). 
Here are some links to separate pages that show you how I load files and images:

- [How to Load Code, Scripts, and Files](https://gitlab.com/duder1966/youtube-projects/-/tree/master/ESP32Mini/v2/code)
- [How to Load a MicroPython Image](https://gitlab.com/duder1966/youtube-projects/-/tree/master/ESP32Mini/v2/bin)

## Built-In Functions

The ESP32Mini comes with software to support any attached board peripherals like blue LED and the RESET.
There are also a lot of convenience functions included for common events such as connecting to WiFi, file and directory management, and using the Real-Time-Clock.

Most of the class names are self-explanatory, but be sure to have a look at the obscure ones like **st**, which has lots of handy functions for exploring the file system, and **esp32**, which has some *esp32-specific* functions.

### esp32mini
ESP32Mini **Help** and information.
- `esp32mini.info` - ESP32Mini version data.
- `esp32mini.help` - List ESP32Mini extra modules.
- `esp32mini.show(module=None)` - List functions for a given module based on the **string** name (i.e. use quotes)

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

### rtc
**Real-Time Clock** functions. 
- `rtc.ntp_set()` - Set local time using network time server. Requires an established WiFi connection. May time out without setting (not sure why at this point). If it fails, let the connection stabilize and try again.
- `rtc.set(datetime_tuple)` - Set local time manually. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.get()` - Get local time as a tuple of numbers. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.linux_epoch` - Get the Linux epoch time integer (seconds since Jan 1 1970). Differs from ESP32 time stamp.
- `rtc.dtstamp` - Get local time as a string: `2021-05-27 18:42:35 UTC`

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

 
