import json
import urllib2
import time

url = 'http://multime.ga/temp/set.php?json='

for temp in range (60, 79):

    date = time.strftime("%Y-%m-%d")
    hours = time.strftime("%H")
    minutes = time.strftime("%M")
    seconds = time.strftime("%S")

    encodedJson = '%5B%7B%22date%22%3A%22' + date + '+' + hours + '%3A' + minutes + '%3A' + seconds + '%22%2C+%22value%22%3A%22' + str(temp) + '%22%7D%5D'
    fullUrl = url + encodedJson
    print fullUrl
    urllib2.urlopen(fullUrl).read();

    time.sleep(10)

#[{"date":"2015-11-25 12:45:11", "value":"55"}]
