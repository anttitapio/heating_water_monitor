# Installation

1. Add following lines to /etc/rc.local

sudo modprobe w1-gpio
sudo modprobe w1-therm
/usr/bin/python <full path to tempRead.py> &

2. Add AWS credential information to /etc/boto.cfg

[Credentials]
aws_access_key_id = <AKIA........>
aws_secret_access_key = <Tlc............>

3. Install pip, boto
