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
GPIO.setup(26, GPIO.OUT)
GPIO.setup(DrainBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DrainBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
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

def Valve(dir):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        OnOff = GPIO.input(5)
        ValveD = GPIO.input(6)
        if dir != ValveD:
                if ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.LOW)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                time.sleep(1)
                        GPIO.output(5, GPIO.HIGH)
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.HIGH)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                time.sleep(1)
                        GPIO.output(5, GPIO.HIGH)

def dbRead(table):
                Farm = mysql.connector.connect(
                                host="localhost",

                                user="pi",
                                passwd="a-51d41e",
                                database="Farm"
                )
                cursor = Farm.cursor()
                if table == "H2O":
                        cursor.execute("select * from Farm.H2O ORDER BY date DESC LIMIT 1")
                        myresult = cursor.fetchone()
                        cursor.close
                        try:
                                date = myresult[0]
                                Temp = myresult[1]
                                pH = myresult[2]
                                EC = myresult[3]
                                TDS = myresult[4]
                                S = myresult[5]
                                SG = myresult[6]
                                return date, Temp, pH, EC, TDS, S, SG
                        except TypeError:
                                pass
                if table == "Shed":
                        cursor.execute("select * from Farm.Shed ORDER BY date DESC LIMIT 1")
                        myresult = cursor.fetchone()
                        cursor.close
                        try:
                                date = myresult[0]
                                mode = myresult[1]
                                period = myresult[2]
                                LastFlood = myresult[3]
                                NextFlood = myresult[4]
                                return date, mode, period, LastFlood, NextFlood
                        except TypeError:
                                pass
                if table == "Data":
                        cursor.execute("select * from Farm.farmdata ORDER BY date DESC LIMIT 1")
                        myresult = cursor.fetchone()
                        cursor.close
                        try:
                                date = myresult[0]
                                main = myresult[1]
                                lights = myresult[2]
                                ExFan = myresult[3]
                                AirPump = myresult[4]
                                WaterPump = myresult[5]
                                ValveS = myresult[6]
                                ValveD = myresult[7]
                                return date, main, lights, ExFan, AirPump, WaterPump, ValveS, ValveD
                        except TypeError:
                                pass
                if table == "VolDrain":
                        cursor.execute("select * from Farm.VolDrain ORDER BY date DESC LIMIT 1")
                        myresult = cursor.fetchone()
                        cursor.close
                        try:
                                date = myresult[0]
                                HD1 = myresult[1]
                                Hall1 = myresult[2]
                                HD2 = myresult[3]
                                Hall2 = myresult[4]
                                HD3 = myresult[5]
                                Hall3 = myresult[6]
                                HD4 = myresult[7]
                                Hall4 = myresult[8]
                                VolBed1 = myresult[9]
                                VolBed2 = myresult[10]
                                return date,HD1,Hall1,HD2,Hall2,HD3,Hall3,HD4,Hall4,VolBed1,VolBed2
                        except TypeError:
                                pass



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
	PStatus = GPIO.input(21)
	now = datetime.now()
	Shed=dbRead('Shed')
	period = Shed[2]
	LastFlood = Shed[3]
        NextFlood = Shed[4]
	SinceLast = now-LastFlood
	SinceLastMin = SinceLast.seconds / 60
	if Date > NextFlood:
		if not PStatus and flow1 == 0 and flow2 == 0:
			Valve(0)
			GPIO.output(26, GPIO.HIGH)
		        GPIO.output(21, GPIO.HIGH)
		value = ""
		now = datetime.now()
		T = now.strftime("%H:%M:%S")
		Sensor = ""
		os.system('clear')
		PStatus = GPIO.input(21)	
		print T 
		print ""
		if PStatus:
			Pstatus = "On"
		else:
			Pstatus = "Off"
		print "Pump: ", Pstatus
		print "Pump Bed1 Volume: ", flow3,"L"
		print "Drain Bed1 Volume: ", flow1,"L\t", flow1b,"L"
		print ""
		print "Pump Bed2 Volume: ", flow4,"L"
		print "Drain Bed2 Volume: ", flow2,"L\t", flow2b,"L"
		time.sleep(0.3)
	#	Sensor = ""
		if flow1 > 1:
			GPIO.output(21, GPIO.LOW)
			time.sleep(1)
			if flow1 > 1.003:
				Valve(1)
				GPIO.output(21, GPIO.HIGH)
			else:
				GPIO.output(21, GPIO.HIGH)
		if flow2 > 1:
			GPIO.output(21, GPIO.LOW)
			time.sleep(1)
	                if flow2 > 1.003:
				GPIO.output(21, GPIO.LOW)
			else:
				GPIO.output(21, GPIO.HIGH)
    except KeyboardInterrupt:
	
        print '\ncaught keyboard interrupt!, bye'
        GPIO.cleanup()
        sys.exit()
