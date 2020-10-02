#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys
from datetime import datetime
FLOW_SENSOR = 22
FLOW_SENSOR2 = 23
FLOW_SENSOR3 = 24
FLOW_SENSOR4 = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
global option
#option = "a"
global count1
global count2
global count3
global count4
count1 = 0
count2 = 0
count3 = 0
count4 = 0
def countPulse(channel):
	global count1
	global count2
	global count3
	global count4
	now = datetime.now()
	T = now.strftime("%H:%M:%S")
	if option == "1" or option == "a":
		if channel == 22:
			channel = "Drain 1"
			count1 = count1 + 1
			flow1 = count1 / (60 * 7.5)
			print T, channel, count1, flow1
        if option == "2" or option == "a":
		if channel == 23:
			channel = "Drain 2"
		        count2 = count2 + 1
			flow2 = count2 / (60 * 7.5)
			print T, channel, count2, flow2
        if option == "3" or option == "a":
		if channel == 24:
			channel = "Pump 1"
		        count3 = count3 + 1
			flow3 = count3 / (60 * 7.5)
			print T, channel, count3, flow3
	if option == "4" or option == "a":
	        if channel == 25:
			channel = "Pump 2"
		        count4 = count4 + 1
			flow4 = count4 / (60 * 7.5)
			print T, channel, count4, flow4

GPIO.add_event_detect(FLOW_SENSOR, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(FLOW_SENSOR2, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(FLOW_SENSOR3, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(FLOW_SENSOR4, GPIO.FALLING, callback=countPulse)
try:
	option = sys.argv[1]
except:
	option = "a"

while True:
    try:
        time.sleep(1)

    except KeyboardInterrupt:
        print '\ncaught keyboard interrupt!, bye'
        GPIO.cleanup()
        sys.exit()
