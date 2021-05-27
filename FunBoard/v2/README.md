# This Directory

- **applications** - this contains application code from YouTube videos which use the FunBoard V2
- **images** - this contains the last MicroPython image tested using FunBoard V2 code
- **code** - this contains the code you need to run the FunBoard V1 (should be pre-loaded)

# Documentation

A work in progress.

## Connecting

### Putty

Coming soon to a theater near you.

### Picocom

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

### Python + PySerial

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

## Built In Functions

The FunBoard comes with software to support all of the attached board peripherals like the MicroSD card, the leds, beeper, etc.
There are also a lot of convenience functions included for common events such as connecting to WiFi, file and directory management, and using the Real-Time-Clock.

Most of the class names are self-explanatory, but be sure to have a look at the obscure ones like **st**, which has lots of handy functions for exploring the file system, and **esp32**, which has some *esp32-specific* functions.

### beeper
- `beeper.beep(freq=None,secs=None,vol=None,duty=None)`
- `beeper.beepn(count=1,freq=None,secs=None,vol=None,duty=None,wait=None)`
- `beeper.beep2(freq=None,freq2=None,secs=None,vol=None,duty=None,fcps=100)`
- `beeper.play(notestring=None,root=None,beat=None,vol=None,duty=None)`

### funboard
- `funboard.info`
- `funboard.help`
- `funboard.show(module=None)`

### esp32
- `esp32.reset`
- `esp32.temp`
- `esp32.tempf`
- `esp32.hall`
- `esp32.memory`
- `esp32.flash`

## eziot
- `eziot.stats()`
- `eziot.watch(startrows=10,update=10,group=None,device=None)`
- `eziot.post_data(group=None,device=None,data1=None,data2=None,data3=None,data4=None)`
- `eziot.get_data(count=1,after=None,group=None,device=None)`
- `eziot.delete_data(rowids=[],before=None,xall=False)`

### led
Control the blue LED.
- `led.on()` - Turn the blue LED on.
- `led.off()` - Turn the blue LED off.
- `led.blink(count=1,ontime=None,offtime=None)` - Blink the blue LED. You can set the number of blinks using `count=n`. You can also set the `ontime` and `offtime` in milliseconds. Defaults are on for 50ms and off for 250ms.
- `led.pwmx(force=False)` - Turn of pulse-width modulation (see below). You can also use `led.off()`.
- `led.pwm(percent=100)` - Turn on blue LED using pulse-width modulation. This allows you to control brightness. Provide an integer percent from 0 (off) to 100 (full brightness).
- `led.pwm2(start=0,end=100,pause=10)` - Progressive change of blue LED from `start` percent to `end` percent, pause `pause` milliseconds between steps (sets how long the transition tales). This allow a fade in, fade out option.

### pixels
- `pixels.off()`
- `pixels.kill()`
- `pixels.set_brightness(brightness=0)`
- `pixels.get_color(color,brightness=None)`
- `pixels.setp(pixel,color,brightness=None,write=True)`
- `pixels.sweep(color=None,brightness=None,ontime=25,offtime=5)`

### rtc
Real-Time Clock functions. 
- `rtc.ntp_set()` - Set local time using network time server. Requires an established WiFi connection. May time out without setting (not sure why at this point). If it fails, let the connection stabilize and try again.
- `rtc.set(datetime_tuple)` - Set local time manually. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.get()` - Get local time as a tuple of numbers. `datetime_tuple = (year,month,day,hours,minutes,seconds)`
- `rtc.linux_epoch` - Get the Linux epoch time integer (seconds since Jan 1 1970). Differs from ESP32 time stamp.
- `rtc.dtstamp` - Get local time as a string: `2021-05-27 18:42:35 UTC`

### sdcard
- `sdcard.error(e=None,s='SDCard not mounted.',unmount=False)`
- `sdcard.sdpath(path=None)`
- `sdcard.mount()`
- `sdcard.unmount(show=True)`
- `sdcard.format(warn=True)`

## st
- `st.abspath(fd=None)`
- `st.isfile(f)`
- `st.isdir(d)`
- `st.exists(fd)`
- `st.tree(d=None,i=0)`
- `st.mkdir(d)`
- `st.remove(f)`
- `st.rmdir(d,root=False)`
- `st.pf(f)`
- `st.printfile(f)`
- `st.pp(obj,depth=0,indentline=True,newline=True,end='\n')`
- `st.ps(obj,depth=0,indentline=True,newline=True,jsonify=False)`
- `st.reload(module)`
- `st.du(d=None,h='MB',show=True,rt=False)`
- `st.memp(show=True,collect=True,rt=False)`

### wifi
- `wifi.scan()`
- `wifi.connect(essid=None,password=None,timeout=15)`
- `wifi.disconnect(timeout=15)`

 
