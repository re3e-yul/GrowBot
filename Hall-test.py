#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys, os
from datetime import datetime
import math
Pump = 21
Valve = 5
VDir = 6
DrainBed1 = 22
DrainBed2 = 18
PumpBed1 = 24
PumpBed2 = 25
Pump = 21
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DrainBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DrainBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Pump, GPIO.IN)
global option
global T
global count1
global count2
global count3
global count4
global flow1
global flow1b
global flow2
global flow2b
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
flow1b = 0
flow2 = 0
flow2b = 0
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
	global flow1b
        global flow2
        global flow2b
        global flow3
        global flow4
	global Sensor
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
	if (channel == DrainBed1):
			Sensor = "Drain 1"
			count1 = count1 + 1
			count3 = count3 - 1
			flow1 = round((count1 / (60 * 28.3906)),3)
			flow1b = round((count3 / (60 * 28.3906)),3)
	if (channel == DrainBed2):
			Sensor = "Drain 2"
		        count2 = count2 + 1
			count4 = count4 - 1
			flow2 = round(count2 / (60 * 28.3906),3)
			flow2b = round(count4 / (60 * 28.3906),3)
	if (channel == PumpBed1):
			Sensor = "Pump 1"
		        count3 = count3 + 1
			flow3 = round(count3 / (60 * 28.3906),3)
        if (channel == PumpBed2):
			Sensor = "Pump 2"
		        count4 = count4 + 1
			flow4 = round(count4 / (60 * 28.3906),3)

GPIO.add_event_detect(DrainBed1, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(DrainBed2, GPIO.RISING, callback=countPulse)
GPIO.add_event_detect(PumpBed1, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(PumpBed2, GPIO.FALLING, callback=countPulse)
try:
	option = sys.argv[1]
except:
	option = "a"

while True:
    try:
	value = ""
	now = datetime.now()
	T = now.strftime("%H:%M:%S")
	Sensor = ""
	os.system('clear')
	PStatus = GPIO.input(21)	
	print T , Sensor
	print ""
	if PStatus:
		PStatus == "On"
	else:
		PStatus == "Off"
	print "Pump: ", PStatus
	print "Pump Bed1 Volume: ", flow3,"L"
	print "Drain Bed1 Volume: ", flow1,"L\t", flow1b,"L"
	print ""
	print "Pump Bed2 Volume: ", flow4,"L"
	print "Drain Bed2 Volume: ", flow2,"L\t", flow2b,"L"
	time.sleep(0.3)
#	Sensor = ""
    except KeyboardInterrupt:
	
        print '\ncaught keyboard interrupt!, bye'
        GPIO.cleanup()
        sys.exit()
