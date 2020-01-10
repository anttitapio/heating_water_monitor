# Description
The code is intented for a Raspberry Pi.
It queries temperatures of DS18B20-sensor and sends a mail to list of recipients if the temperature is below a set limit.
The limits are currently hardcoded constants with default values corresponding my specific application of monitoring my heating water temperature.

# Installation
## Raspberry pi 4
1. Enable one-wire interface
2. Run setup.sh <gmail account for alarm mail sending> <pw>

## Raspberry pi 2
1. Run setup.sh <gmail account for alarm mail sending> <pw>
2. Add following lines to /etc/rc.local
sudo modprobe w1-gpio
sudo modprobe w1-therm
