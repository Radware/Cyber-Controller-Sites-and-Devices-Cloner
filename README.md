# Cyber-Controller-Sites-and-Devices-Cloner #
This tool will copy all Cyber Controller objects (sites, Alteon devices, DefensePro devices) to another Cyber Controller.

## Table Of Contents ###
- [Description](#description)
- [How To Use](#how-to-use)
- [Currently Supported](#currently-supported)
- [Radware KB](#Radware-KB)
- [Disclaimer](#Disclaimer)

## Description ##
The script described is provided to help with migration for organizations that want to copy sites and devices from a Cyber-Controller instance to another one.

The tool is designed to copy Alteon and DefensePro devices.

The tool works for both physical and virtual devices.

The tool changes the name of the root site if needed for both the **Physical Containers** and **Sites and Devices sections**.


## How To Use ##
Verify that Python3.10 or later is installed on your computer.
The script uses the following modules:
* requests
* time
* urllib3
* json
* os
* getpass
* logging

Example how to get the files using git command:
```
# git clone https://github.com/Radware/Cyber-Controller-Sites-and-Devices-Cloner.git
# cd Cyber-Controller-Sites-and-Devices-Cloner
```
To execute the script, you can either double-click on the file or run it through the terminal.

Example how to run the it from the terminal:
```
# python3.10 copy_cyber_controller_objects.py
```

Follow the terminal instructions and provide the source and destination cyber controller details.

After the script finishes running, you can refer the log file **copy_cyber_controller_objects.log** in the current directory

## Currently Supported ##
* Site objects
* Physical and virtual Alteon devices
* Physical and virtual Defense-Pro devices

## Radware KB ##
Will be published soon.

## Disclaimer ##
There is no warranty, expressed or implied, associated with this product. Use at your own risk.
