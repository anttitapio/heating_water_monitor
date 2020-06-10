#!/usr/bin/env python3

import json
import datetime
import time
import os
import yagmail
from subprocess import call
from systemd import journal

SENSOR_CORRECTION_CONSTANT = 7.0 # align to analog meter
ALARMING_LEVEL = 72.0
MEASUREMENT_INTERVAL =  5 * 60 #seconds
OWN_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_LOG_FILE = OWN_DIR + "/tempRead.log"
APP_LOG_FILE = OWN_DIR + "/application.log"
MAIL_USER = os.environ['GM_USER']
MAIL_PASS = os.environ['GM_PASS']
MAIL_HEADER = 'Kattila sammunut: t='
MAIL_RECEIVER_FILE = OWN_DIR + "/mail_recipients.txt"
yag = yagmail.SMTP(MAIL_USER, MAIL_PASS)

def init_sensor():
    #Check the serial number of the attached sensor
    #TODO if sensor not attached
    #TODO multiple sensors
    call(["touch", OWN_DIR + "/devicenames.txt"])
    deviceNamesFile = open(OWN_DIR + "/devicenames.txt", "w")
    call(["find", "/sys/bus/w1/devices", "-name", "28-*"],
         stdout=deviceNamesFile)
    deviceNamesFile.close()

    deviceNamesFile = open(OWN_DIR + "/devicenames.txt")
    deviceDirectory = deviceNamesFile.read()
    deviceNamesFile.close()
    call(["rm", "-f", OWN_DIR + "/devicenames.txt"])
    log("Device initialized at " + get_date_and_time())
    log("Measurements will be read from " + deviceDirectory.rstrip() + "/w1_slave")

    return deviceDirectory.rstrip() + "/w1_slave"


def read_mail_recipients_from_file():
    recipients = []
    with open (MAIL_RECEIVER_FILE, "r") as fileHandler:
        for line in fileHandler:
            recipients.append(line.strip())
    return recipients


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
    recipients = read_mail_recipients_from_file()
    for recipient in recipients:
        try:
            yag.send(recipient, MAIL_HEADER + tempAsString, 'empty')
        except Exception as e:
            log("Error in sending mail: " + str(e))
        else:    
            log("Mail sent to " + recipient + ": " + tempAsString)


def log(log_entry, log_file = APP_LOG_FILE):
    logFile = open(log_file, "a")
    logfile_entry = get_date_and_time() + ': ' + log_entry + '\n'
    logFile.write(logfile_entry)
    logFile.close()
    journal.write(log_entry)


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
                consecutiveAlarms = 0
            else:
                log("Temp value still low, waiting " + str(10 - consecutiveAlarms) \
                    + " rounds before sending a new mail")
            consecutiveAlarms = consecutiveAlarms + 1
        else:
            consecutiveAlarms = 0

        time.sleep(MEASUREMENT_INTERVAL)


pathToSensorData = init_sensor()
main_loop()
