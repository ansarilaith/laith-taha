# Images
Here you can find images that can be loaded to the ESP32Mini V2. There are basically two types of images you will find here: basic Micropython images (copies from the MicroPython website), and ESP32Mini images, which I make.

- `esp32mini_xxxxxxxx.bin` - Images starting with **esp32mini_** contains both the MicroPython binary and the ESP32Mini library. This is an all-in-one package. You should be able to load it, hit the reset button, and hear/see the default boot sequence. These images will be larger than plain MicroPython images, typically 3 to 4 MB.

- `esp32-idf3-xxxxxxxx.bin` - Images starting with **esp32-idf** contain just MicroPython binary. Once loaded, you will be able to connect to the REPL and use MicroPython. You will need to load the ESP32Mini code as well to take advantage of all board perripherals.

# Requirements
Before getting started...

You will also need to have access to serial ports. For Linux, you will need to do something like this:
```
sudo adduser my_username dialout
```
You have to log out and back in or reboot after changing dialout.

You need the `esptool.py' module from Espressif:
```
python3 -m pip install esptool
```

You need to know where (what port) the ESP32Mini is connected. In Linux you can do something like this:
```
ls -hal /dev | grep ttyUSB
```

# Erase the Flash
Erasing the flash is not required, but it is a good idea if you are loading a MicroPython image for the first time. This will remove the MicroPython as well as any scripts you have loaded. It's basically a clean slate to start with.

- Connect to the ESP32Mini via a USB-serial cable. 
- Put the ESP32Mini into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- You can now erase the flash using the following (set the correct port):
```
esptool.py --port /dev/ttyUSB0 erase_flash
```

- Now push the **RESET** button.

# Load The Image
After you choose one of the above images (or download one from the MicroPython website), this is how you can load it to your ESP32Mini.

- Change to the directory containing the `bin` file you want to load.
- Connect to the ESP32Mini via a USB-serial cable.
- Put the ESP32Mini into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- Now you can write/re-write the image using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -z 0x1000 the_image_file_i_want.bin
```
- Now push the **RESET** button. Ready to go.

# Reading/Saving and Image
You may want to read the flash from one ESP32 and write it to another. This will allow you to make a copy without having to first load MicroPython and then load the ESP32Mini scripts. This is how I create the `esp32mini_xxxxxxxx.bin` images you can find here. 

- Change to the directory where you want to store the `bin` file you create.
- Connect to the ESP32Mini via a USB-serial cable.
- Put the ESP32Mini into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- You can now read the full ESP32 flash image (MicroPython and ESP32Mini code) using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 read_flash 0x1000 0x3ff000 esp32mini_20211212.bin
```
- Push the **RESET** button to get out of program mode.

These images will be about 4MB (4096 bytes less). You can trim the `0xFF` bytes from the end of the file if you want (and know how to do it), but it isn't necessary.

You can actually use any hex address range for the read. Range `0x1000` to `0x3ff000` creates a file that 1) can be loaded the same as a MicroPython image, and 2) includes the full 4MB of usable flash on the ESP32Mini ESP32 module.



