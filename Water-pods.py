#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys, os
from datetime import datetime
import datetime as DT
import math
import mysql.connector

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
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
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
			flow3 = round(count3 / (60 * 28.3906),3)
        if (channel == PumpBed2) and VDir == 1 and PStatus == 1:
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



def Display():
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
	print "Drain Bed1 Volume: ", flow1,"L"
	print ""
	print "Pump Bed2 Volume: ", flow4,"L"
	print "Drain Bed2 Volume: ", flow2,"L"
	time.sleep(0.3)

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
                                HallSensor()
                                Display()
                        GPIO.output(5, GPIO.HIGH)
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.HIGH)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                HallSensor()
                                Display()
                        GPIO.output(5, GPIO.HIGH)

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
        if Oflow3 == flow3:
#		print "nothin pod1"
		data = (now, now, "0", HD2, h2, now, "0", HD4, h4 ,flow3, flow4)
		Display()
        else:
                if Oflow3 < flow3:
#			print "filling pod1"
			data = (now, HD1,h1, HD2, h2, now, "1",HD4 , "0", flow3, flow4) #FILL bed 1
			Display()
                else:
#			print "draining pod1"
			data = (now, now, "1", HD2, h2, HD3, "0",HD4, h4, flow3, flow4)   #DRAIN bed1
			Display()
        if Oflow4 == flow4:
#		print "nothin pod2"
		data = (now, HD1, h1, now, "0", HD3, h3, now, "0", flow3, flow4)
		Display()
        else:
                if Oflow4 < flow4:
#			print "filling pod2"
			data = (now, HD1,h1, HD2, h2, HD3, "0", now, "1", flow3, flow4) #FILL bed 2
			Display()
   		else:
#			print "draining pod2"
			data = (now, HD1,h1,now, "1", HD3, h3, HD4, "0", flow3, flow4)  #DRAIN bed2
			Display()

	try:
                DV.execute(sql, data)
        except:
                pass
        DV.close
        Farm.commit()
        Farm.close

	Oflow3 = flow3
	Oflow4 = flow4
	time.sleep(1)

def Light():
        Shed=dbRead('Shed')
        try:
                mode = Shed[1]
        except:
                mode = "Vegetative"
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        LStatus = GPIO.input(12)
        if mode == "Flowering":
                DayStart = "08:00:00"
                DayEnd = "18:55:00"
        else:
                mode = "Vegetative"
                DayStart = "08:00:00"
                DayEnd = "19:00:00"

        if now > DayStart  and  now < DayEnd:
                if not LStatus:
                        GPIO.output(26, GPIO.HIGH)
                        GPIO.output(12, GPIO.HIGH)
                        DataWrite()
        else:
                if LStatus:
                        GPIO.output(12, GPIO.LOW)
                        DataWrite()


def Flood():
	global LastFlood
	global NextFlood
	global Sensor
	PStatus = GPIO.input(21)
	ValveD = GPIO.input(6)
	now = datetime.now()
	Date = now.strftime("%Y-%m-%d %H:%M:%S")
	Shed=dbRead('Shed')
	date = Shed[0]
	mode = Shed[1]
	period = Shed[2]
	LastFlood = Shed[3]
        NextFlood = Shed[4]
	SinceLast = now-LastFlood
#	print NextFlood
	time.sleep(1)
	if now >= NextFlood:
		Valve(0)
		while Sensor!= "Drain 1":
#		while flow1 < (flow3 / 10 ):
			Display()
			DataWrite()
			GPIO.output(26, GPIO.HIGH)
			GPIO.output(21, GPIO.HIGH)
		timeout = time.time() + 5
		while True:
			Display()
			DataWrite()
    			test = 0
    			if test == 5 or time.time() > timeout:
        			break
    			test = test - 1
		Valve(1)
                while Sensor!= "Drain 2":
#		while flow2 < (flow4 / 10 ):
			Display()
			DataWrite()
			GPIO.output(26, GPIO.HIGH)
                        GPIO.output(21, GPIO.HIGH)
		timeout = time.time() + 5
		while True:
			Display()
			DataWrite()
                        test = 0
                        if test == 5 or time.time() > timeout:
                                break
                        test = test - 1
		GPIO.output(21, GPIO.LOW)
		now = datetime.now()
                NextFlood = now + DT.timedelta(hours = int(period))
                Farm = mysql.connector.connect(
                	host="localhost",
                        user="pi",
                        passwd="a-51d41e",
                        database="Farm"
                        )
                SheD = Farm.cursor() 
		sql = "INSERT INTO Farm.Shed (date, mode, period, LastFlood, NextFlood) VALUES (%s, %s, %s, %s,%s)"
                data = (Date,mode,period,now,NextFlood)
                SheD.execute(sql,data)
                SheD.close
                Farm.commit()
		Farm.close
		Valve(0)
	else:
		GPIO.output(21, GPIO.LOW)

def DataWrite():
                date = datetime.now()
                Date = date.strftime("%Y-%m-%d %H:%M:%S")
                now = date.strftime("%H:%M:%S")
                main = GPIO.input(26)
                Lights = GPIO.input(12)
                APump = GPIO.input(16)
                ExFan = GPIO.input(20)
                WPump = GPIO.input(21)
                ValveS = GPIO.input(5)
                ValveD = GPIO.input(6)

                Act=dbRead('Data')
                LDate = Act[0]
                Lmain = Act[1]
                Llight = Act[2]
                LExFan = Act[3]
                LAPump = Act[4]
                LWPump = Act[5]
                LValveS = Act[6]
                LValveD = Act[7]

                SinceLast = date-LDate
                SinceLastSec = SinceLast.seconds
                if main != Lmain or Lights != Llight or APump != LAPump or ExFan !=LExFan or WPump != LWPump or ValveS != LValveS or ValveD != LValveD:
                        Farm = mysql.connector.connect(
                                        host="localhost",
                                        user="pi",
                                        passwd="a-51d41e",
                                        database="Farm"
                        )

                        SheD = Farm.cursor()
                        sql = "insert INTO Farm.farmdata (date,main,lights,ExFan,AirPump,WaterPump,3wv,3wvD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (Date, main, Lights, ExFan, APump, WPump, ValveS,ValveD)
                        SheD.execute(sql, val)
                        SheD.close
                        Farm.commit()
                        Farm.close



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
	Oflow1 = 0
	Oflow2 = 0
	Oflow3 = 0
	Oflow4 = 0
	while True:
    		try:
			Display()
			Light()
			Flood()
			HallSensor()
    		except KeyboardInterrupt:
	
        		print '\ncaught keyboard interrupt!, bye'
        		GPIO.cleanup()
        		sys.exit()





if __name__=="__main__":

        Main()

