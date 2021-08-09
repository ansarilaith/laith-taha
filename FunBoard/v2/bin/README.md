# Images
Here you can find images that can be loaded to the FunBoard V2. There are basically two types of images you will find here: basic Micropython images (copies from the MicroPython website), and FunBoard images, which I make.

- `funboard_xxxxxxxx.bin` - Images starting with **funboard_** contains both the MicroPython binary and the FunBoard library. This is an all-in-one package. You should be able to load it, hit the reset button, and hear/see the default boot sequence. These images will be larger than plain MicroPython images, typically 3 to 4 MB.

- `esp32-idf3-xxxxxxxx.bin` - Images starting with **esp32-idf** contain just MicroPython binary. Once loaded, you will be able to connect to the REPL and use MicroPython. You will need to load the FunBoard code as well to take advantage of all board perripherals.

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

You need to know where (what port) the FunBoard is connected. In Linux you can do something like this:
```
ls -hal /dev | grep ttyUSB
```

# Erase the Flash
Erasing the flash is not required, but it is a good idea if you are loading a MicroPython image for the first time. This will remove the MicroPython as well as any scripts you have loaded. It's basically a clean slate to start with.

- Connect to the FunBoard via the USB3c cable. 
- Put the FunBoard into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- You can now erase the flash using the following (set the correct port):
```
esptool.py --port /dev/ttyUSB0 erase_flash
```

- Now push the **RESET** button.

# Load The Image
After you choose one of the above images (or download one from the MicroPython website), this is how you can load it to your FunBoard.

- Change to the directory containing the `bin` file you want to load.
- Connect to the FunBoard via the USB3c cable.
- Put the FunBoard into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- Now you can write/re-write the image using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -z 0x1000 the_image_file_i_want.bin
```
- Now push the **RESET** button. Ready to go.

# Reading/Saving and Image
You may want to read the flash from one ESP32 and write it to another. This will allow you to make a copy without having to first load MicroPython and then load the FunBoard scripts. This is how I create the `funboard_xxxxxxxx.bin` images you can find here. 

- Change to the directory where you want to store the `bin` file you create.
- Connect to the FunBoard via the USB3c cable.
- Put the FunBoard into program mode. Hold down the **PROG** button and (while still holding it down) push the **RESET** button.
- You can now read the full ESP32 flash image (MicroPython and FunBoard code) using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 read_flash 0x1000 0x3ff000 funboard_20210528.bin
```
- Push the **RESET** button to get out of program mode.

These images will be about 4MB (4096 bytes less). You can trim the `0xFF` bytes from the end of the file if you want (and know how to do it), but it isn't necessary.

You can actually use any hex address range for the read. Range `0x1000` to `0x3ff000` creates a file that 1) can be loaded the same as a MicroPython image, and 2) includes the full 4MB of usable flash on the FunBoard ESP32 module.



# Full Install and Test Procedure

This is the install and test procedure for new boards. It tests the basic functions of the ESP32 and circuits on the FunBoard.

Here is a video of me going through the install and test sequence: [Install and Test Video](https://www.youtube.com/watch?v=H8-ObIHnE7s&t=50s)

## Procedure

1. Create a **2.4 GHz** Wifi access point with the essid `youressid` and the password `yourpassword`. The access point **MUST HAVE INTERNET ACCESS**. That it, it cannot be unconnected (a dead end) The ESP32 must be able to access the https://eziot.link website.

1. Prepare a micro SDcard (FAT32) with at least 1 file on it. Place it in the Micro SDcard slot on the FunBoard.

1. Download the most recent `install_funboard_20??????.bin` image (see files above).

1. Install `esptool.py` to your desktop computer following the instructions in the [Requirements](#requirements) section above.

1. Connect the FunBoard to your desktop computer via the USBc connector (see [Connecting](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2#connecting)).
The green LED should illuminate.
See **ERROR 4**.

1. Determine which TTY port is being used by the FunBoard connection.
See **ERROR 1**.

1. Load the `.bin` image to the ESP32 following the [Load Image](#load-the-image) instructions above. 
Be sure to set the correct port and `.bin` file name.
See **ERROR 2**.

1. Connect to the FunBoard using `picocom` or a similar terminal program using the correct port (same as for loading).
See [Connecting](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2#connecting).
Initially you will not see any data on the screen from the FunBoard.
However, your terminal program should connect with no errors because the USB connection is being handled by the CP2104 chip.
See **ERROR 1**.

1. Push the `RESET` button on the FunBoard.
The ESP32 should reset (reboot) and start printing data to the terminal.
During the boot sequence, the blue LED should illuminate, sound should be heard, and the MicroPixels should flash.
See **ERROR 3**.

1. The terminal should promp you to begin the test sequence.
This starts by testing the blue LED. 
Press ENTER to begin and follow the screen instructions.
See **ERROR 4**.

1. The next test is for the MicroPixels.
They should illuminate white (or off white) one at a time.
Watch for non-illuminating or non-white MicroPixels.
See **ERROR 5**.

1. The next test is for the buzzer (sound).
You should hear a beep.
See **ERROR 6**.

1. The next test is for the SDcard (which should already be installed).
Check the terminal for the directory tree print out from the SDcard.
You should be able to see the test file you created and its size.
See **ERROR 7**.

1. The next test is for WiFi.
During this test, the ESP32 will 1: scan local access points and print them to the terminal, 2: connect to the access point with essid `youressid`, 3: set the local time using NTP (10 tries), and 4: download data from eziot.link.
If data is downloaded from eziot.link, WiFi is OKAY.
See **ERROR 8**.

1. Finally, you will be prompted to re-write the test version of `main.py` with a regular version.
If all tests have gone as intended, say yes.
If you want to re-run the test sequence, say no.

1. Now push the `RESET` button.
The FunBoard should go through the normal boot sequence but not enter the test sequence.
Watch the screen.
After booting you should end up with a python prompt `>>>`.

## ERRORS

1. If you are unable to determine the port (the TTY connection doesn't register).
If using Windows, insure you have the proper drivers installed (see [Connecting](https://gitlab.com/duder1966/youtube-projects/-/tree/master/FunBoard/v2#connecting)).
You may also need to switch USB ports and/or logout/reboot in order to get the device to register.
If the port will still not register, the error will be associated with the USBc connector or CP2104 chip.

1. If `esptool.py` is unable to connect to the ESP32 on the FunBoard and load the image,
first insure you are using the correct port (the most common mistake).
If you are sure that your load parameters are correct, the error will be associated with the push-button switches and reset circuit.

1. If the boot sequence does not run (data printed to the terminal, blue LED, sound, MicroPixel sweep), the `.bin` image has not been loaded correctly.
The error may be related to the ESP32 flash or RAM memory. Try reloading the the `.bin` image.

1. The green LED should illuminate when power (USBc cable) is connected to the FunBoard.
The blue LED should illuminate during boot and the test sequence.
Failure to illuminate indicates an error with the LED or LED circuit (hardware).

1. Any error with the MicroPixels indicates a hardware issue with the MicroPixel circuit.
If no pixels illuminate, there is probably an issue with the signal or power supply lines.
If a single pixes does not illuminate, it is may be installed (soldered) incorrectly or have internal damage.
If a pixel is not white, it has internal damage.

1. The buzzer should beep (make sounds/music) during the boot sequence and during testing.
Poor sound or no sound indicate circuit error or internal damage.

1. If you are unable to get the SDcard to mount (and you are sure it is inserted correctly),
the first thing to try is formatting it using the built-in FunBoard functions `sdcard.format()` and `sdcard.mount()`.
You may have to try using a different SDcard (try a 4GB or 8GB card).
If you continue to be unable to mount an SDcard, there may be an error with the SPI circuit used to read the card.

1. The ESP32 will be looking for a **2.4 GHz** access point with the exact essid `youressid` and the password `yourpassword`.
The access point **MUST HAVE INTERNET ACCESS**.
Re-check these paramaters (the most commom errors).
If these parameters are met and you are not able to connect and download data from eziot.link, this indicates there is an issue with the WiFi on the ESP32.



























