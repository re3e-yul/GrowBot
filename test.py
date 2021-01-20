#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys, os
from datetime import datetime
import datetime as DT
import math
import mysql.connector
import threading
import io
import fcntl
import syslog
import getpass
import select
DrainBed1 = 25
DrainBed2 = 22
PumpBed1 = 24
PumpBed2 = 23
main = 26
Lights = 12
APump = 16
ExFan = 20
Pump = 21
ValveS = 5
ValveD = 6
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(DrainBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DrainBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(main, GPIO.OUT)
GPIO.setup(Lights, GPIO.OUT)
GPIO.setup(APump, GPIO.OUT)
GPIO.setup(ExFan, GPIO.OUT)
GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(ValveS, GPIO.OUT)
GPIO.setup(ValveD, GPIO.OUT)
global option
global T
global count1
global count2
global count3
global count4
global Oflow1
global Oflow2
global Oflow3
global Oflow4
global flow1
global flow2
global flow3
global flow4
global Sensor
global LastFlood
global NextFlood
T = 0
Sensor = 0
count1 = 0
count2 = 0
count3 = 0
count4 = 0
Oflow1 = 0
Oflow2 = 0
Oflow3 = 0
Oflow4 = 0
flow1 = 0
flow2 = 0
flow3 = 0
flow4 = 0

def Display():
	global Sensor
	if not Sensor:
		Sensor = ""
        os.system('clear')
	now = datetime.now()
        print now.strftime("%d-%m-%Y %H:%M:%S"), Sensor
        print "\t\tPump Bed1 VBed1,: ", flow3,"L"
        print "\t\tPump Bed2 VBed2,: ", flow4,"L"

def countPulse(channel):
        global count1
        global count2
        global count3
        global count4
        global Oflow1
        global Oflow2
        global Oflow3
        global Oflow4
        global flow1
        global flow2
        global flow3
        global flow4
        global Sensor
        VDir = GPIO.input(6)
        PStatus = GPIO.input(21)
        if (channel == DrainBed1):
                        Sensor = "Drain 1"
                        count1 = count1 + 1
                        count3 = count3 - 1
                        flow1 = round((count1 / (60 * 28.3906)),3)
                        flow3 = round(count3 / (60 * 28.3906),3)
        if (channel == DrainBed2):
                        Sensor = "Drain 2"
                        count2 = count2 + 1
                        count4 = count4 - 1
                        flow2 = round(count2 / (60 * 28.3906),3)
                        flow4 = round(count4 / (60 * 28.3906),3)
        if (channel == PumpBed1) and VDir == 0 and PStatus == 1 :
                        Sensor = "Pump 1"
                        count3 = count3 + 1
                        flow3 = round(count3 / (60 * 14.3906),3)
        if (channel == PumpBed2) and VDir == 1 and PStatus == 1:
                        Sensor = "Pump 2"
                        count4 = count4 + 1
                        flow4 = round(count4 / (60 * 22.3906),3)

        if flow3 <= 0:
                flow3 = 0
        if flow4 <= 0:
                flow4 = 0

def HallSensor():

        global Oflow1
        global Oflow2
        global Oflow3
        global Oflow4
        global flow3
        global flow4
        VD=dbRead('VolDrain')
        date = VD[0]
        HD1 = VD[1]
        h1 = VD[2]
        HD2 = VD[3]
        h2 = VD[4]
        HD3 = VD[5]
        h3 = VD[6]
        HD4 = VD[7]
        h4 = VD[8]
        OVBed1 = VD[9]
        OVBed2 = VD[10]
        Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
        DV = Farm.cursor()
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
        Display()
        print "Bed1 : Oflow3:",Oflow3, " ,flow3:",flow3
#       print "Bed2 : Oflow4:",Oflow4, " ,flow4:",flow4
        if flow3 != 0:
                if Oflow3 == flow3:
#                       print "nothin pod1"
                        data = (now, HD1, h1, now, "0", HD3, h3, now, "0", flow3, flow4)
                else:
                        if Oflow3 < flow3:
#                               print "filling pod1"
                                data = (now, HD1,h1, HD2, h2, HD3, "1", now, "0", flow3, flow4) #FILL bed 1
                        else:
#                               print "draining pod1"
                                data = (now, now,"1",HD2, h2, HD3, "0", HD4, h4, flow3, flow4)  #DRAIN bed1

        if flow4 != 0:
                if Oflow4 == flow4:
#                       print "nothin pod2"
                        data = (now, HD1, h1, now, "0", HD3, h3, now, "0", flow3, flow4)
                else:
                        if Oflow4 < flow4:
#                               print "filling pod2"
                                data = (now, HD1,h1, HD2, h2, HD3, "0", now, "1", flow3, flow4) #FILL bed 2
                        else:
#                               print "draining pod2"
                                data = (now, HD1,h1,now, "1", HD3, h3, HD4, "0", flow3, flow4)  #DRAIN bed2
        try:
                DV.execute(sql, data)
        except:
                pass
        DV.close
        Farm.commit()
        Farm.close
        Oflow3 = flow3
        Oflow4 = flow4
#       time.sleep(1.5)

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
                        Farm.close
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
                        Farm.close
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
                        Farm.close
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
                        Farm.close
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
                if table == "Cal":
                        cursor.execute("select * from Farm.Cal ORDER BY date DESC LIMIT 1")
                        myresult = cursor.fetchone()
                        cursor.close  
                        Farm.close
                        try:
                                date = myresult[0]
                                pHDelta = myresult[1]
                                ECDelta = myresult[2]
                                DpHp = myresult[3]
                                VpHp = myresult[4]
                                DpHm = myresult[5]
                                VpHm = myresult[6]
                                DFloA = myresult[7]
                                VFloA = myresult[8]
                                DFloB = myresult[9]
                                VFloB = myresult[10]
                                DVegA = myresult[11]
                                VVegA = myresult[12]
                                DVegB = myresult[13]
                                VVegB = myresult[14]
                                return date,pHDelta,ECDelta,DpHp,VpHp,DpHm,VpHm,DFloA,VFloA,DFloB,VFloB,DVegA,VVegA,DVegB,VVegB
                        except TypeError:
                                pass
                Farm.close



def Main():
	while True:

		try:
        		GPIO.add_event_detect(DrainBed1, GPIO.RISING, callback=countPulse)
        	except:
        		pass
 		try:
        		GPIO.add_event_detect(DrainBed2, GPIO.RISING, callback=countPulse)
		except:
        		pass
        	try:
		        GPIO.add_event_detect(PumpBed1, GPIO.RISING, callback=countPulse)
        	except:
        		pass
        	try:
        	        GPIO.add_event_detect(PumpBed2, GPIO.RISING, callback=countPulse)
        	except:
                	pass
		HallSensor()
        	Display()



if __name__=="__main__":

        Main()


