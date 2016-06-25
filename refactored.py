import json
import urllib2
import time
from subprocess import call

CORRECTION_LEVEL = 7.0 # align to analog meter
ALARMING_LEVEL = 65.0
MEASUREMENT_INTERVAL = 5 * 60 #seconds
DB_WRITE_URL = 'http://tempread.netai.net/temp/set.php?json='
HTTP_TIMEOUT_SECONDS = 30

errorCount = 0
alarmRaisedInARowCount = 0

def init_sensor():
    #check the serial number of the attached sensor
    #TODO if sensor not attached
    #TODO multiple sensors

    call(["touch", "/home/pi/devicenames.txt"])
    deviceNamesFile = open("/home/pi/devicenames.txt", "w")
    call(["find", "/sys/bus/w1/devices", "-name", "28-*"], stdout=deviceNamesFile)
    deviceNamesFile.close()

    deviceNamesFile = open("/home/pi/devicenames.txt")
    deviceDirectory = deviceNamesFile.read()
    deviceNamesFile.close()
    pathToSensorData = deviceDirectory.rstrip() + "/w1_slave"
    call(["rm", "-f", "/home/pi/devicenames.txt"])

def read_temp():
    tfile = open(pathToSensorData)
    text = tfile.read()
    tfile.close()
    # Split the text with new lines (\n) and select the second line.
    secondline = text.split("\n")[1]
    # Split the line into words, referring to the spaces, and select
    # the 10th word (counting from 0).
    temperatureData = secondline.split(" ")[9]
    # The first two characters are "t=", so get rid of those and convert the
    # temperature from a string to a number.
    temperature = float(temperatureData[2:])
    return (temperature / 1000) + CORRECTION_LEVEL

def main_loop():
    while 1:
        logFile = open("/home/pi/tempRead.log", "a")

        tempAsString = "%2.1f" % read_temp()

        if temperature < ALARMING_LEVEL:
            print 'Alarming level'
            print tempAsString
            if (alarmRaisedInARowCount % 10) == 0:
                call(["/home/pi/heating_water_monitor/mail-script.sh",
                     tempAsString])
            alarmRaisedInARowCount += 1
        else:
            alarmRaisedInARowCount = 0

        date = time.strftime("%Y-%m-%d")
        hours = time.strftime("%H")
        minutes = time.strftime("%M")
        seconds = time.strftime("%S")

        output = tempAsString + ' ' + date + ' ' + hours + ':' + minutes + ':'
            + seconds + '\n'
        logFile.write(output)
        print output
        encodedJson = '%5B%7B%22date%22%3A%22' + date + '+' + hours + '%3A'
            + minutes + '%3A' + seconds + '%22%2C+%22value%22%3A%22'
            + tempAsString + '%22%7D%5D'

        fullUrl = DB_WRITE_URL + encodedJson
        try:
            urllib2.urlopen(fullUrl, timeout=HTTP_TIMEOUT_SECONDS).read();
        except Exception:
            errorCount = errorCount + 1
            errorLine = "Server error while connecting. Happened %d times since"
                        + " service start.\n" % errorCount
            logFile.write(errorLine)
            print errorLine

        logFile.close()
        time.sleep(MEASUREMENT_INTERVAL)

init_sensor()
main_loop()

#[{"date":"2015-11-25 12:45:11", "value":"55"}]
