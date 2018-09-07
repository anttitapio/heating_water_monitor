import json
import boto3 # for aws db
import urllib2
import datetime
import time
from subprocess import call

SENSOR_CORRECTION_CONSTANT = 7.0 # align to analog meter
ALARMING_LEVEL = 65.0
MEASUREMENT_INTERVAL =  5 * 60 #seconds
DB_ADD_URL = "https://dynamodb.us-west-2.amazonaws.com"
TEMP_LOG_FILE = "/home/pi/tempRead.log"
APP_LOG_FILE = "/home/pi/application.log"


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
    log("Device initialized at " + get_date_and_time())
    log("Measurements will be read from " + deviceDirectory.rstrip() + "/w1_slave")

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
    return datetime.datetime.now().isoformat()


def send_mail(tempAsString):
    call(["/home/pi/heating_water_monitor/mail-script.sh", tempAsString])


def upload_result_to_db(timestamp, temp):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url=DB_ADD_URL)
    table = dynamodb.Table('temperature_data')
    response = table.put_item(
        Item={
            'sensor_location' : 'incoming_heating',
            'timestamp' : timestamp,
            'temperature' : temp
            }
    )
    log("DB upload response: " + json.dumps(response, indent = 4))


def log(log_entry, log_file = APP_LOG_FILE):
    logFile = open(log_file, "a")
    log_entry = get_date_and_time() + ': ' + log_entry + '\n'
    logFile.write(log_entry)
    logFile.close()


def main_loop():
    consecutiveAlarms = 0
    while True:
        temperature = read_temp()
        tempAsString = "%2.1f" % temperature
        log(tempAsString, TEMP_LOG_FILE)
        if temperature < ALARMING_LEVEL:
            if (consecutiveAlarms % 10) == 0:
                log("Low temperature read (" + tempAsString + "), sending mail")
                send_mail(tempAsString)
                log("Mail sent: " + tempAsString)
                consecutiveAlarms = 0
            else:
                log("Temp value still low, waiting " + str(10 - consecutiveAlarms) \
                    + " rounds before sending a new mail")
            consecutiveAlarms = consecutiveAlarms + 1
        else:
            log("Normal temperature read (" + tempAsString + ")")
            consecutiveAlarms = 0

        upload_result_to_db(get_date_and_time(), tempAsString)

        time.sleep(MEASUREMENT_INTERVAL)


pathToSensorData = init_sensor()
main_loop()
