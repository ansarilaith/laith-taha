# Images

- `funboard_xxxxxxxx.bin` - Images starting with **funboard_** contains both the MicroPython binary and the FunBoard library. This is an all-in-one package. You should be able to load it, hit the reset button, and hear/see the default boot sequence. These images will be larger than plain MicroPython images, typically 3 to 4 MB.

- `esp32-idf3-xxxxxxxx.bin` - Images starting with **esp32-idf** contain just MicroPython binary. Once loaded, you will be able to connect to the REPL and use MicroPython. You will need to load the FunBoard code as well to take advantage of all board perripherals.

# Requirements

You will also need to have access to serial ports. For Linux, you will need to do something like this:
```
sudo adduser my_username dialout
```
You have to log out and back in or reboot after changing dialout.

You need the `esptool.py' module from Espressif:

```
python3 -m pip install esptool
```

You need to know where (what port) the FunBoard is connected. In Linux you can do something like this:
```
ls -hal /dev | grep ttyUSB
```

- Change to the directory containing the `bin` file you want to load.
- Connect to the FunBoard via the USB3c cable.

# Erase the Flash

To put the FunBoard into program mode, hold down the **PROG** button and (while still holding it down) push the **RESET** button.

You can now erase the flash using the following (set the correct port):
```
esptool.py --port /dev/ttyUSB0 erase_flash
```

Now push the **RESET** button.

# Load The Image

To put the FunBoard into program mode, hold down the **PROG** button and (while still holding it down) push the **RESET** button.

Now you can write/re-write the image using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -z 0x1000 the_image_file_i_want.bin
```
Now push the **RESET** button. Ready to go.

# Reading/Saving and Image

To put the FunBoard into program mode, hold down the **PROG** button and (while still holding it down) push the **RESET** button.

You can now read the full ESP32 flash image (MicroPython and FunBoard code) using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 read_flash 0x1000 0x3ff000 my_image_file.bin
```

Now push the **RESET** button to get out of program mode.

You can actually use any hex address range for the read. Range `0x1000` to `0x3ff000` creates a file that 1) can be loaded the same as a MicroPython image, and 2) includes the full 4MB of usable flash on the FunBoard ESP32 module.

The image might be longer than needed (almost a full 4MB). It will probably be padded with `0xFF`. The Python script `ffrstrip.py` will r-strip the `0xFF` from the file end and might make it smaller. You need to test the image as a training `0xFF` could possibly be significant.
```
python3 ffrstrip.py my_image_file.bin my_image_file_stripped.bin
```











