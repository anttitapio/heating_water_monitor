import json
import urllib2
import time
from subprocess import call

correctionLevel = 7.0 # align to analog meter
alarmingLevel = 65.0
measurementInterval = 60*5 #seconds
url = 'http://tempread.netai.net/temp/set.php?json='

errorCount = 0
alarmRaisedInARowCount = 0
#check the serial number of the attached sensor
call(["touch", "/home/pi/devicenames.txt"])
deviceNamesFile = open("/home/pi/devicenames.txt", "w")

#TODO if sensor not attached
call(["find", "/sys/bus/w1/devices", "-name", "28-*"], stdout=deviceNamesFile)
deviceNamesFile.close()
deviceNamesFile = open("/home/pi/devicenames.txt")
#TODO multiple sensors
deviceDirectory = deviceNamesFile.read()
deviceNamesFile.close()
pathToSensorData = deviceDirectory.rstrip() + "/w1_slave"
call(["rm", "-f", "/home/pi/devicenames.txt"])

while 1:
    tfile = open(pathToSensorData)
    text = tfile.read()
    tfile.close()
    # Split the text with new lines (\n) and select the second line.
    secondline = text.split("\n")[1]
    # Split the line into words, referring to the spaces, and select the 10th word (counting from 0).
    temperaturedata = secondline.split(" ")[9]
    # The first two characters are "t=", so get rid of those and convert the temperature from a string to a number.
    temperature = float(temperaturedata[2:])
    temperature = (temperature / 1000) + correctionLevel

    tempAsString = "%2.1f" % temperature

    if temperature < alarmingLevel:
        print 'Alarming level'
        print tempAsString
        if (alarmRaisedInARowCount % 10) == 0:
            call(["/home/pi/heating_water_monitor/mail-script.sh", tempAsString])
        alarmRaisedInARowCount += 1
    else:
        alarmRaisedInARowCount = 0

    date = time.strftime("%Y-%m-%d")
    hours = time.strftime("%H")
    minutes = time.strftime("%M")
    seconds = time.strftime("%S")

    print tempAsString + ' ' + date + ' ' + hours + ':' + minutes + ':' + seconds

    encodedJson = '%5B%7B%22date%22%3A%22' + date + '+' + hours + '%3A' + minutes + '%3A' + seconds + '%22%2C+%22value%22%3A%22' + tempAsString + '%22%7D%5D'
    fullUrl = url + encodedJson
    try:
        urllib2.urlopen(fullUrl).read();
    except Exception:
        errorCount = errorCount + 1
        print "Server error while connecting. Happened %d times since service start." % errorCount

    time.sleep(measurementInterval)

#[{"date":"2015-11-25 12:45:11", "value":"55"}]
