# REPLace.py ESP32 Uploader

This will load scripts to an ESP32 via the REPL serial link.

## Setup

Put this script in the directory where your files are.
It will walk into all the subdirs looking for files.

You need PySerial: `python3 -m pip install pyserial`.
You also need to have permission to use the serial port.
On Linux you will have to do something like `sudo adduser myusername dialout`, and then logout-login again.

Recommended to install mpy-cross: `python3 -m pip install mpy-cross`.
If installed, REPLace.py it will also pre-compile `.py` files to `.mpy` for you.
Be sure to delete the `.py` files on the ESP (they will run instead of the compiled ones).

## Basic Usage

You can call it with `python3 REPLace.py` (or `./REPLace.py` on Linux).
It will try some default ports, but it is easier just to specify the correct port using `-p /dev/ttyUSB1`, especially if you have several devices.

Here are the basics I use most:
```
# see the help
./REPLace.py -h

# load all files with -a
./REPLace.py -p /dev/ttyUSB0 -a

# load select files with -i
./REPLace.py -p /dev/ttyUSB0 -i main.py micropix.py

```
