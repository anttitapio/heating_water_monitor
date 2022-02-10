#!/usr/bin/env python3

import json
import datetime
import time
import os
import yagmail
from subprocess import call
from systemd import journal
from collections import deque

#class yag():
#    def send(self, recipient, header, body):
#        print("Sending mail to {}, header: {}, body: {}", recipient, header, body)

SENSOR_CORRECTION_CONSTANT = 7.0 # align to analog meter
ALARMING_LEVEL = 75.0
MEASUREMENT_INTERVAL =  6 * 60 #seconds
OWN_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_LOG_FILE = OWN_DIR + "/tempRead.log"
TEMP_INIT_VALUE = 0
ALLOWED_TEMP_DROP = 0.11
APP_LOG_FILE = OWN_DIR + "/application.log"
WEB_PAGE_FILE = OWN_DIR + "/index.html"
MAIL_USER = os.environ['GM_USER']
MAIL_PASS = os.environ['GM_PASS']
MAIL_HEADER_ALARM = 'Kattila sammunut, lämpötila laskussa: '
MAIL_HEADER_OK = 'Kattila sytytetty, lämpotila nousussa: '
MAIL_PREFIX = 'Viimeisin mittaukset: \n'
MAIL_RECEIVER_FILE = OWN_DIR + "/mail_recipients.txt"
yag = yagmail.SMTP(MAIL_USER, MAIL_PASS)
logQue = deque(['']*10, maxlen=10)

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


def send_mail(tempAsString, mailHeader):
    recipients = read_mail_recipients_from_file()
    mailbody = ''
    for line in logQue:
        mailbody += line
    for recipient in recipients:
        try:
            yag.send(recipient, mailHeader + tempAsString, MAIL_PREFIX + mailbody)
        except Exception as e:
            log("Error in sending mail: " + str(e))
        else:    
            log("Mail sent to " + recipient + ": " + tempAsString)


def log(log_entry, log_file = APP_LOG_FILE):
    logFile = open(log_file, "a")
    logfile_entry = get_date_and_time() + ': ' + log_entry + '\n'
    logFile.write(logfile_entry)
    logFile.close()
    if log_file == TEMP_LOG_FILE:
        logQue.appendleft(logfile_entry)
        webFile = open(WEB_PAGE_FILE, "w")
        for line in logQue:
            webFile.write(line + '<br>')
        webFile.close()
    else:
        journal.write(log_entry)


def main_loop():
    consecutiveAlarms = 0
    temperature = TEMP_INIT_VALUE
    alarm = False
    while True:
        previousTemperature = temperature
        previousTempAsString = "%2.1f" % temperature
        temperature = read_temp()
        tempAsString = "%2.1f" % temperature
        log(tempAsString, TEMP_LOG_FILE)
        if temperature < ALARMING_LEVEL:
            if temperature > previousTemperature:
                if alarm:
                    send_mail(tempAsString, MAIL_HEADER_OK)
                    log("Temperature rising after alarm (" + tempAsString + "), "
                        + " sending ok mail and seizing alarm")
                elif previousTemperature != TEMP_INIT_VALUE:
                    log("Temperature still low but rising, (" + previousTempAsString
                        + " -> " + tempAsString + "), no new alarm")
                alarm = False
                continue

            if (previousTemperature - temperature) > ALLOWED_TEMP_DROP:
                if alarm == False:
                    consecutiveAlarms = 0
                alarm = True
                log("Temperature falling (" + previousTempAsString + " -> "
                    + tempAsString + "), setting alarm")
            else:
                log("Temperature low, no change (" + tempAsString + "), no new alarm")

            if alarm and (consecutiveAlarms % 10) == 0:
                log("Sending mail alarm")
                send_mail(tempAsString, MAIL_HEADER_ALARM)
                consecutiveAlarms = 0
            elif alarm:
                log("Alarm active, waiting "
                    + str(10 - consecutiveAlarms)
                    + " rounds before sending a new mail")
            if alarm:
                consecutiveAlarms += 1
        else:
            log("Temperature at normal level (" + tempAsString + ")")
            alarm = False
            consecutiveAlarms = 0

        time.sleep(MEASUREMENT_INTERVAL)


pathToSensorData = init_sensor()
main_loop()
