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
###############################
def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier
###############################
def countPulse(channel):
	global count1
	global count2
	global count3
	global count4
	global flow1
	global flow2
	global flow3
	global flow4
	global Sensor
	Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
	now = datetime.now()
        VD=dbRead('VolDrain')
        Hall1 = VD[1]
        Hall2 = VD[2]
        Hall3 = VD[3]
        Hall4 = VD[4]
        Bed1vol = VD[5]
        Bed2vol = VD[6]

    	if channel == 24:
                        Sensor = "Pump 1"
                        count1 = count1 + 1
                        Bed1vol = round(count1 / (60 * 7.5),3)
                        sql = "INSERT INTO Farm.VolDrain (date,Hall1,Hall2,Hall3,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        val = (now,Hall1,Hall2,"1",Hall4,Bed1vol,Bed2vol)
        ###############
        #             #
        #  Bed1 Drain #
        #             #
        ###############	
	if channel == 22:
                        Sensor = "Drain 1"
                        count1 = count1 - 1
                        Bed1vol = round(count1 / (60 * 7.5),3)
                        sql = "INSERT INTO Farm.VolDrain (date,Hall1,Hall2,Hall3,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        val = (now,"1",Hall2,Hall3,Hall4,Bed1vol,Bed2vol)

	###############
        #             #
        #  Bed2 Fill  #
        #             #
        ###############
	if channel == 25:
			Sensor = "Pump 2"
			count2 = count2 + 1
			Bed2vol = round((count2 / (60 * 7.5)),3)
			sql = "INSERT INTO Farm.VolDrain (date,Hall1,Hall2,Hall3,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s, %s, %s, %s)"
	                val = (now,Hall1,Hall2,Hall3,"1",Bed1vol,Bed2vol)
	
	###############
        #             #
        #  Bed2 Drain #
        #             #
        ###############
	if channel == 23:
                        Sensor = "Drain 2"
                        count2 = count2 - 1
                        Bed2vol = round(count2 / (60 * 7.5),3)
                        sql = "INSERT INTO Farm.VolDrain (date,Hall1,Hall2,Hall3,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        val = (now,Hall1,"1",Hall3,Hall4,Bed1vol,Bed2vol)
    	DV.execute(sql, val)
    	DV.close
    	Farm.commit()




###############################
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
            BedVol = myresult[7]
            return date, Temp, pH, EC, TDS, S, SG, BedVol
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
            Hall = myresult[8]
            return date, main, lights, ExFan, AirPump, WaterPump, ValveS, ValveD, Hall
        except TypeError:
            pass
    if table == "VolDrain":
        cursor.execute("select * from Farm.VolDrain ORDER BY date DESC LIMIT 1")
        myresult = cursor.fetchone()
        cursor.close
        try:
            date = myresult[0]
            Hall1 = myresult[1]
            Hall2 = myresult[2]
            Hall3 = myresult[3]
            Hall4 = myresult[4]
            VolBed1 = myresult[5]
            VolBed2 = myresult[6]
            return date, Hall1, Hall2, Hall3, Hall4, VolBed1, VolBed2
        except TypeError:
            pass

def main():
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
		except KeyboardInterrupt:
        		print '\ncaught keyboard interrupt!, bye'
        		GPIO.cleanup()
        		sys.exit()


if __name__=="__main__":
   main()

