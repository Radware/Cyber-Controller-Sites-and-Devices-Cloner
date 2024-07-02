# Cyber-Controller-Sites-and-Devices-Cloner #
This tool will copy all Cyber Controller objects (sites, Alteon devices, DefensePro devices) to another Cyber Controller.

## Table Of Contents ###
- [Description](#description)
- [How To Use](#how-to-use)
- [Currently Supported](#currently-supported)
- [Radware KB](#"Radware KB")

## Description ##
The following script is provided to help with migration for organizations that want to copy sites and devices from a Cyber-Controller to another one.
The tool is designed to copy Alteon devices and Defense-Pros.
The tool will work for both physical and virtual devices.

## How To Use ##
In order to use the script make sure you have installed python3.10 or above
The script uses the following modules:
* time
* requests
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
Example hoe to run the it from the terminal:
```
python3.10 copy_cyber_controller_objects.py
```

Follow the terminal instructions and provide the source and destination cyber controller details.
After the script finishes you can view the log file in the directory.
The log file is:
**copy_cyber_controller_objects.log**

## Currently Supported ##
* Sites
* Alteon physical and virtual devices
* Defense Pro physical and virtual devices

## Radware KB ##
https://radware.com
