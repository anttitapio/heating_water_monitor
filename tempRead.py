import json
import boto3 # for aws db
import urllib2
import time
from subprocess import call

SENSOR_CORRECTION_CONSTANT = 7.0 # align to analog meter
ALARMING_LEVEL = 65.0
MEASUREMENT_INTERVAL = 5 #seconds
DB_ADD_URL = "https://dynamodb.us-west-2.amazonaws.com"
HTTP_TIMEOUT_SECONDS = 30

consecutiveAlarms = 0

def init_sensor():
    #Check the serial number of the attached sensor
    #TODO if sensor not attached
    #TODO multiple sensors
    call(["touch", "/home/pi/devicenames.txt"])
    deviceNamesFile = open("/home/pi/devicenames.txt", "w")
    call(["find", "/sys/bus/w1/devices", "-name", "28-*"],
         stdout=deviceNamesFile)
    deviceNamesFile.close()

    deviceNamesFile = open("/home/pi/devicenames.txt")
    deviceDirectory = deviceNamesFile.read()
    deviceNamesFile.close()
    call(["rm", "-f", "/home/pi/devicenames.txt"])

    return deviceDirectory.rstrip() + "/w1_slave"

def read_temp():
    tfile = open(pathToSensorData)
    text = tfile.read()
    tfile.close()
    # Split the text with new lines (\n) and select the second line.
    secondline = text.split("\n")[1]
    # Split the line into words, referring to the spaces, and select
    # the 10th word (counting from 0).
    temperaturedata = secondline.split(" ")[9]
    # The first two characters are "t=", so get rid of those and
    # convert the temperature from a string to a number.
    temperature = float(temperaturedata[2:])

    return (temperature / 1000) + SENSOR_CORRECTION_CONSTANT

def get_date_and_time():
    date = time.strftime("%Y-%m-%d")
    hours = time.strftime("%H")
    minutes = time.strftime("%M")
    seconds = time.strftime("%S")

    return date + ' ' + hours + ':' + minutes + ':' + seconds

def get_json_string(time, temperature):
        encodedJson = '%5B%7B%22date%22%3A%22' + time('date') + '+' + \
            time('hours') + '%3A' + time('minutes') + '%3A' + time('seconds') + \
            '%22%2C+%22value%22%3A%22' + temperature + '%22%7D%5D'

def raise_alarm():
    if (consecutiveAlarms % 10) == 0:
        call(["/home/pi/heating_water_monitor/mail-script.sh", tempAsString])
        consecutiveAlarms += 1
    else:
        consecutiveAlarms = 0

def upload_result_to_db(date, temp):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url=DB_ADD_URL)
    table = dynamodb.Table('tempLog')
    response = table.put_item(
        Item={
            'Time' : date,
            'Temperature' : temp
            }
    )
    print(json.dumps(response, indent=4))

def main_loop():
    while True:
        #TIME!
        logFile = open("/home/pi/tempRead.log", "a")
        temperature = read_temp()
        tempAsString = "%2.1f" % temperature

        if temperature < ALARMING_LEVEL:
            print 'Alarming level'
            print tempAsString
            raise_alarm()

        log_entry = get_date_and_time() + ' ' + tempAsString + '\n'
        logFile.write(log_entry)
        upload_result_to_db(get_date_and_time(), tempAsString)
        logFile.close()

        time.sleep(MEASUREMENT_INTERVAL)


pathToSensorData = init_sensor()
main_loop()

#[{"date":"2015-11-25 12:45:11", "value":"55"}]