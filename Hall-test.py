#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys, os
from datetime import datetime
import math
FLOW_SENSOR = 22
FLOW_SENSOR2 = 23
FLOW_SENSOR3 = 24
FLOW_SENSOR4 = 25
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(FLOW_SENSOR4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
global option
global T
global count1
global count2
global count3
global count4
global flow1
global flow2
global flow3
global flow4
global Sensor
T = 0
Sensor = 0
count1 = 0
count2 = 0
count3 = 0
count4 = 0
flow1 = 0
flow2 = 0
flow3 = 0
flow4 = 0
def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier

def countPulse(channel):
#	global T
#	T = 0
	global count1
	global count2
	global count3
	global count4
	global flow1
        global flow2
        global flow3
        global flow4
	global Sensor
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
	if channel == 22:
			Sensor = "Drain 1"
			count1 = count1 + 1
			flow1 = round((count1 / (60 * 7.5)),3)
	if channel == 23:
			Sensor = "Drain 2"
		        count2 = count2 + 1
			flow2 = round(count2 / (60 * 7.5),3)
	if channel == 24:
			Sensor = "Pump 1"
		        count3 = count3 + 1
			flow3 = round(count3 / (60 * 7.5),3)
        if channel == 25:
			Sensor = "Pump 2"
		        count4 = count4 + 1
			flow4 = round(count4 / (60 * 7.5),3)

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
	now = datetime.now()
	T = now.strftime("%H:%M:%S")
	os.system('clear')
	
	print T , Sensor
	print ""
	print "Pump Bed1 Hits  :", count3, "Volume: ", flow3,"L"
	print "Drain Bed1 Hits :", count1, "Volume: ", flow1,"L"
	print ""
	print "Pump Bed2 Hits  :", count4, "Volume: ", flow4,"L"
	print "Drain Bed2 Hits :", count2, "Volume: ", flow2,"L"

	time.sleep(0.3)
#	Sensor = ""
    except KeyboardInterrupt:
        print '\ncaught keyboard interrupt!, bye'
        GPIO.cleanup()
        sys.exit()
