# Introduction

**Note:** I'm just starting to write these docs. Keep checking back.

## What is EZIoT.link?

The `eziot.link` website and application is an online location that IoT developers and hobbyiest can use to post data from their IoT devices. The posted data can then be downloaded and used by other IoT devices or desktop applications. 

The Python file `eziot.py` is a script that can be run with both **Python3** and **MicroPython**. It functions as a Software Development Kit or **SDK** that allows the user to easily interact with the Application Programming Interface or **API** on the `eziot.link` website.

By adding the SDK to MicroPython-based projects and devices, users can easily swap data between devices and desktop applications. The `eziot.link` website is basically a cloud data platform where you can drop off your data package so that it can be picked up later by your other devices. 

![EZIoT.link Illustration](https://eziot.link/images/eziot_illustration_1.png)

## What Can I Do?

The `eziot.py` SDK in combination with the `eziot.link` API will allow your upload data from anywhere with an internet connection and use it anywhere else with an internet connection. Here are some of the specific things you can do:

1. **Upload Data** - You can upload up to **1024** rows of data. For each row of data you can include **6** items or values: `[group,device,data1,data2,data3,data4]`. The first 5 values can be strings (i.e. text), integers, or floats. If the value is a string, it can be up to **32** characters long. The `data4` value is the same, except that if it is a string, it can be **256** characters long. If you load more than 1024 rows, the oldest row will be dropped from the data and the new row will be added. Also, the `eziot.link` API will add a time stamp, an id number, and an IP address to the row, so you don't need to worry about that.

1. **Download Data** - Once you have some data, you can easily get it back. You can easliy download the latest rows (newest data). You can request 1 to 1024 rows, and you can select on `group` and `device`. So it you want to get the most recent row for the `command` group and the `FunBoard1` device, no problem. If you need to do something fancy, just grab all your rows and do what you need.

1. **Delete Data** - It's your data. You can delete any row, or any row older than a given row, or all of it. Whatever you need. I don't care. I don't want it.

1. **Pass Data Between Devices** - You can easily send commands to devices and pass data between devices by using the `group` and `device` values. Just post data using a specific group and device, and then the target device can get that data using the same group and device. Easy.

## What Can't I Do?

The `eziot.link` API is designed handle what most developers and hobbyists need: an interim place to post and get data. It will probably handle 90% of IoT applications. But just to be clear, here are some of the things you shouldn't expect from `eziot.link`:

1. **Unlimited Data** - Nope. This is a place to post data so you can get it and use it some other place, not save it forever. You get 1024 rows to work with. If you need to save all data forever, then periodically download it to your desktop.

1. **Huge Data** - Nope. You only get 6 fields to post data, and only one allows a long string. So, you can post temperatures, counts, status, et cetera, and if you need you can put some JSON into `data4` field. That's mainly what IoT needs to do. And don't forget that the `eziot.link` API will add those extras line timestamps.

1. **User Support** - It's a super-simple, basically-free, service. It's also tested and known to work if used as intended. It's being used everyday by people all over the place. If your having trouble, the best bet is to read the docs again.

## What About Privacy and Security?

1. The `eziot.link` website and API is not interested in collecting your data. Your data is intended to be transient and exists in only one location, and when you delete it, or if it gets dropped off the bottom of the stack, then it's gone forever. Don't ask about recovering it because it can't be done. There are no backups. Anything that needs to be maintained should be downloaded to your desktop soon after it is posted.

1. The `eziot.link` website and API does collect data necessary to maintain a web server. Access logs (which include IP addresses) are maintained (but not for very long). We also, of course, keep the email address you used to create an account for the period that the account exists (until you delete it).

1. The `eziot.link` website and API **SHOULD NOT** be used to host any data that is critical to commercial, medical, government, or military systems or infrastructure. This is an experimental site/application designed for developers and hobbyists. There is no guarantee of permanence for data or application. Both may be removed at any time.

1. The `eziot.link` website and API **SHOULD NOT** be used to host any data that is personal or private in nature. We use encryption on the front end, but not on the back end. That is, your data is encrypted when transmitted over the internet (if you are using HTTPS), but it is not stored in an encrypted format. Please keep this in mind.

# EZIoT SDK Documentation

## A Video to Get Started

To be added soon.

## No Installation

### Python Versions

**Python:** Developed on 3.8. Should work on 3.5+.

**MicroPython:** Developed on 1.13. Should work on 1.1+.

### Setup Requirements

The EZIoT.link SDK script itself does not need installation. Simply copy/load it to a location in your Python or MicroPython `import` path list (see `sys.path`).

The SDK used the `requests` or `urequests` module to send and receive data. This is included with most current versions of Python/Micropython.

## Test Run









## Getting an Account


## Functions
The SDK only has a few common commands plus a few extras for convenience.

### Rate Limits

### Posting Data

**Best Practice:** Only post what is needed. Don't hog bandwidth posting useless information.

### Getting Data

**Best Practice:** Only download the rows your need. Use rowids to limit your downloads and not re-download.

### Deleting Data
### Getting Stats
### Sending Commands
### Wifi Connections

The SDK includes several MicroPython WiFi functions as a convenience: 

### Getting Credentials
### Deleting Credentials/Account

**Important:** If you delete your credentials, everything on the server will be lost. All data, all knowledge that you ever has an account.




