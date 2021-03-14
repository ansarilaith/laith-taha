# EZToT Toolkit

I'm starting to write these docs. Keep checking back.

## What is EZIoT? 

The file `eziot.py` is a script that will run with both Python3 and MicroPython. It functions as a **S**oftware **D**evelopment **K**it or **SDK** that allows the user to easily interact with the **A**pplication **P**rogramming **I**nterface or **API** on the `eziot.link` website.

The **API** on the `eziot.link` website allows users to create an account where they can easily upload data from their internet-connected projects and devices. The uploaded data can then be downloaded and used by your other devices or your desktop. The `eziot.link` website is basically a cloud location where you can drop off your data so that it can be picked up later by your other devices. 

![EZIoT.link Illustration](https://eziot.link/images/eziot_illustration_1.png)

## What Can I Do?

The `eziot.py` SDK in combination with the `eziot.link` API will allow your upload data from anywhere with an internet connection and use it anywhere else with an internet connection. Here are some of the specific things you can do:

1. **Upload Data** - You can upload up to **1024** rows of data. For each row of data you can include **6** items or values: `[group_name,device_name,data1,data2,data3,data4]`. The first 5 values can be strings (i.e. text), integers, or floats. If the value is a string, it can be up to **32** characters long. The `data4` value is the same, except that if it is a string, it can be **256** characters long. If you load more than 1024 rows, the oldest row will be dropped from the data and the new row will be added.

1. **Download Data** - Once you have some data, you can easily get it back. You can easliy download the latest rows (newest data). You can request 1 to 1024 rows, and you can select on `group` and `device`. So it you want to get the most recent row for the `command` group and the `FunBoard1` device, no problem. If you need to do something fancy, just grab all your rows and do what you need.

1. **Delete Data** - It's your data. You can delete any row, or any row older than a given row, or all of it. Whatever you need.

1. **Pass Data Between Devices** - 

1. **Delete Your Account** - You can also delete everything, as if you never existed on the server. We don't want or need to keep any of your data.

## What should i write next?





