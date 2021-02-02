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
context=getpass.getuser()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  
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
global flow1
global flow2
global flow3
global flow4
global Oflow3
global Oflow4
global Sensor
global LastFlood
global NextFlood
global period
global avg24h
global avg5min
global pHdiff
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
Oflow3 = 0
Oflow4 = 0
avg24h = ""
avg5min = ""
pHdiff = ""
def Main():
	if context == "root":
		thread = ReadSensors(pHECT)
		thread2 = Water(Pump)
		thread3 = ExcCalib(Calibrate)
		thread3 = Water(Pump)
		Deamonstat = os.system('systemctl is-active  growbot')
		if Deamonstat == 768 or Deamonstat == "inactive":
			Deamonstat = "UserLand"
			os.system('systemctl start growbot')
		elif Deamonstat == 0 or Deamonstat == "active":
			Deamonstat = "Deamon"
		else:
			Deamonstat = Deamonstat
	while True:
		if context == "pi":
#			while True:
	                        Display()
		elif context == "root": # and Deamonstat == "Deamon":

			if thread.is_alive() is False:
        	                threadStat = "not running"
                	        print "starting Chemical sensors task"
                        	thread = ReadSensors(pHECT) 
	                        thread.setDaemon(True)
        	                thread.start()
			else:
                                threadStat = "running"
			
			if thread2.is_alive() is False:
                                threadStat2 = "not running"
                                print "starting Watering task"
                                thread2 = Water(Pump)
                                thread2.setDaemon(True)
                                thread2.start()
                                
                        if thread3.is_alive() is False:
                                threadStat3 = "not running"
                                print "starting aut-calibration task"
                                thread3 = ExcCalib(Calibrate)
                                thread3.setDaemon(True)
                                thread3.start()
			
                	else:
                        	threadStat3 = "running"
#			try:
#				GPIO.add_event_detect(DrainBed1, GPIO.BOTH, callback=countPulse1)
#			except:
#				pass
#			try:
#				GPIO.add_event_detect(DrainBed2, GPIO.BOTH, callback=countPulse2)
#			except:
#				pass
#			try:
#				GPIO.add_event_detect(PumpBed1, GPIO.BOTH, callback=countPulse1)
#			except:
#				pass
#			try:
#				GPIO.add_event_detect(PumpBed2, GPIO.BOTH, callback=countPulse2)	
#			except:
#				pass
                        Light()
 #                       Flood()
                        HallReset()
			LogString="Deamonstat: " + Deamonstat + " ,Chem thread: " + threadStat + " ,Cal thread: " + threadStat2
	                LogString=str(LogString)
        	        syslog.syslog(syslog.LOG_INFO,LogString)

class ReadSensors(threading.Thread):
        def __init__(self, Read_Chem_Sensors):
                threading.Thread.__init__(self)
                self.runnable = Read_Chem_Sensors
        def run(self):
                self.runnable()

class ExcCalib(threading.Thread):
        def __init__(self, Exec_Chem_Cal):
                threading.Thread.__init__(self)
                self.runnable = Exec_Chem_Cal
        def run(self):
                self.runnable()

class Water(threading.Thread)
	def __init__(self, Exec_Water):
		threading.Thread.__init__(self)
                self.runnable = Exec_Water
        def run(self):
                self.runnable()	

def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier

def countPulse1(channel):
	global count1
	global count2
	global count3
	global count4
	global flow1
        global flow2
        global flow3
        global flow4
        global Oflow3
        global Oflow4
	global Sensor
	VDir = GPIO.input(6)
	PStatus = GPIO.input(21)
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
        VolBed1 = VD[9]
        VolBed2 = VD[10]
 
        try:
                Farm = mysql.connector.connect(
                        host="192.168.1.14",
                        user="pi",
                        passwd="a-51d41e",
                        database="Farm"
                )
        except:
                pass
        DV = Farm.cursor()
        now = datetime.now()
        Date = now.strftime("%Y-%m-%d %H:%M:%S")
        PStatus = GPIO.input(21)
        sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"

        if (channel == PumpBed1) and VDir == 0 and PStatus == 1 :
                Sensor = "Pump 0"
		if VolBed1 != 0:
                	count3=VolBed1 * 10 + 3.53
		else:
	                count3 = count3 + 3.53
                flow3 = round(count3 / 10,4)
                data = (Date, HD1,"0", HD2, h2, Date, "1", HD4, "0", flow3, VolBed2)  #Filling bed 1

	elif (channel == DrainBed1):
		Sensor = "Drain 0"
		count1 = count1 + 3.53
		if count3 > 1:
			count3 = count3 - 4.53
		else:
			count3 = 0
		flow1 = round((count1 / 10),4)
		flow3 = round((count3 / 10),4)
		data = (Date, Date, "1", HD2, h2, HD3, h3, HD4, h4, flow3, VolBed2)  #Draining bed1
	if Sensor and flow3 > 0:
		Sensor = str(Sensor)
		flow3 = str(flow3)
        	LogString="Hall Sensor: " + Sensor + " :" + flow3
                LogString=str(LogString)
                syslog.syslog(syslog.LOG_INFO,LogString)

        try:
	        DV.execute(sql, data)
	        DV.close
	        Farm.commit()
        except:
                pass
	if flow3 <= -0.1:
		flow3 = 0
	Oflow3 = flow3
def countPulse2(channel):
	global count1
	global count2
	global count3
	global count4
	global flow1
        global flow2
        global flow3
        global flow4
        global Oflow3
        global Oflow4
	global Sensor
	VDir = GPIO.input(6)
	PStatus = GPIO.input(21)
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
        VolBed1 = VD[9]
        VolBed2 = VD[10]
 	
        try:
                Farm = mysql.connector.connect(
                        host="192.168.1.14",
                        user="pi",
                        passwd="a-51d41e",
                        database="Farm"
                )
        except:
                pass
	HallReset()
        DV = Farm.cursor()
        now = datetime.now()
        Date = now.strftime("%Y-%m-%d %H:%M:%S")
        PStatus = GPIO.input(21)
        sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"

        if (channel == PumpBed2) and VDir == 1 and PStatus == 1:
			Sensor = "Pump 1"
			if VolBed1 != 0:
	                        count4=VolBed2 * 10 + 1.87
        	        else:
			        count4 = count4 + 1.87
			flow4 = round(count4 / 10,4)
			data = (Date, HD1,h1, HD2, "0", HD3, "0", Date, "1", VolBed1, flow4)  # filling bed 2
        elif (channel == DrainBed2):
                        Sensor = "Drain 1"
                        count2 = count2 + 1.37
                        if count4 > 0.3:
                                count4 = count4 -0.97
                        else:
                                count4 = 0
                        flow2 = round(count2 / 10,4)
                        flow4 = round(count4 / 10,4)
                        data = (Date, HD1,h1,Date, "1", HD3, h3, HD4, "0", VolBed1, flow4)    # draining bed 2

	try:
	        DV.execute(sql, data)
	        DV.close
	        Farm.commit()
        except:
                pass
	if Sensor and flow4 > 0:
		Sensor = str(Sensor)
                flow4 = str(flow4)
		LogString="Hall Sensor: " + Sensor + " ," + flow4

        	LogString=str(LogString)
	        syslog.syslog(syslog.LOG_INFO,LogString)
	if flow4 <= -0.1:
                flow4 = 0
	flow4 =  str(flow4)
		
def HallReset():
	SinceLastHD1 = 0
        SinceLastHD1Sec = 0
        SinceLastHD2 = 0
        SinceLastHD2Sec = 0
        SinceLastHD3 = 0
        SinceLastHD3Sec = 0
        SinceLastHD4 = 0
        SinceLastHD4Sec = 0
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
        VolBed1 = VD[9]
        VolBed2 = VD[10]
	now = datetime.now()
	SinceLast = (now - date)
	SinceLastSec = SinceLast.seconds
	SinceLastHD1 = (now - HD1)
	SinceLastHD1Sec = SinceLastHD1.seconds
	SinceLastHD2 = (now - HD2)
	SinceLastHD2Sec = SinceLastHD2.seconds
	SinceLastHD3 = (now - HD3)
	SinceLastHD3Sec = SinceLastHD3.seconds
	SinceLastHD4 = (now - HD4)
	SinceLastHD4Sec = SinceLastHD4.seconds
	try:
	        Farm = mysql.connector.connect(
              	        host="192.168.1.14",
                       	user="pi",
                        passwd="a-51d41e",
       	                database="Farm"
               	)
		DV = Farm.cursor()
		sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
		if (h1 or h2 or h3 or h4) and SinceLastSec > 25:
			data = (now, HD1, "0", HD2, "0", HD3, "0", HD4, "0", "0", "0")
			LogString="Hall Sensor: all CLEAR"
		elif Oflow3 == flow3 and (SinceLastHD1Sec > 15 or SinceLastHD3Sec > 15):
		#elif Oflow3 == flow3 and (h1 or h3):
                       	data = (now, HD1, "0", HD2, h2, HD3, "0", HD4, h4, "0", flow4)
			LogString="Hall Sensor: Bed1 CLEAR"
		       	flow3 = 0	
		elif Oflow4 == flow4 and (SinceLastHD2Sec > 15 or SinceLastHD4Sec > 15):
		#elif Oflow4 == flow4 and (h2 or h4):
                       	data = (now, HD1, h1, HD2, "0", HD3, h3, HD4, "0", flow3, "0")
			LogString="Hall Sensor: Bed2 CLEAR"
			flow4 = 0
                DV.execute(sql, data)
       	        DV.close
       	        Farm.commit()
        	LogString=str(LogString)
	        syslog.syslog(syslog.LOG_INFO,LogString)

       	except:
       	        pass


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
			LogString="Lights ON"
	                syslog.syslog(syslog.LOG_INFO,LogString)
        else:
                if LStatus:
                        GPIO.output(12, GPIO.LOW)
        		DataWrite()
			LogString="Lights: OFF"
			LogString=str(LogString)
	                syslog.syslog(syslog.LOG_INFO,LogString) 


def Flood():
	global LastFlood
	global NextFlood
	global period
	global Sensor
	try:
		GPIO.add_event_detect(DrainBed1, GPIO.BOTH, callback=countPulse1)
	except:
		pass
	try:
		GPIO.add_event_detect(DrainBed2, GPIO.BOTH, callback=countPulse2)
	except:
		pass
	try:
		GPIO.add_event_detect(PumpBed1, GPIO.BOTH, callback=countPulse1)
	except:
		pass
	try:
		GPIO.add_event_detect(PumpBed2, GPIO.BOTH, callback=countPulse2)	
	except:
		pass
	
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
	if now >= NextFlood:
		Valve(0)
		LogString="Pump: Flooding Bed 0"
                LogString=str(LogString)
                syslog.syslog(syslog.LOG_INFO,LogString)
		while Sensor!= "Drain 0": # and flow1 < (flow3 / 50):
			GPIO.output(26, GPIO.HIGH)
			GPIO.output(21, GPIO.HIGH)
			DataWrite()
		try:
			flow1 = float(flow1)
			flow3 = float(flow3)
		except:
			flow1 = 0
			flow3 = 0
		while  flow1 < (flow3 / 100) or flow1 == '0':
			DataWrite()
			HallReset()
			LogString="Pump: Draining Bed 0"
        	        LogString=str(LogString)
	                syslog.syslog(syslog.LOG_INFO,LogString)
		Valve(1)
		GPIO.output(21, GPIO.HIGH)
		LogString="Pump: Flooding Bed 1"
                LogString=str(LogString)
                syslog.syslog(syslog.LOG_INFO,LogString)
		while Sensor!= "Drain 1": # and flow2 < (flow4 / 50):
			DataWrite()
			HallReset()
			GPIO.output(26, GPIO.HIGH)
		        GPIO.output(21, GPIO.HIGH)
		while flow2 < 0.5:
			DataWrite()
			HallReset()
			LogString="Pump: Draining Bed 1"
                        LogString=str(LogString)
                        syslog.syslog(syslog.LOG_INFO,LogString)
		GPIO.output(21, GPIO.LOW)
		now = datetime.now()
                NextFlood = now + DT.timedelta(hours = int(period))
                Farm = mysql.connector.connect(
                	host="192.168.1.14",
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
		flow1 == 0
        	flow2 == 0
        	flow3 == 0
	        flow4 == 0
	else:
		GPIO.output(21, GPIO.LOW)
	DataWrite()
	HallReset()
		
def Valve(dir):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        OnOff = GPIO.input(5)
        ValveD = GPIO.input(6)
        if dir != ValveD:
		LogString="3Way Valve: Moving to bed " + str(dir)
                LogString=str(LogString)
                syslog.syslog(syslog.LOG_INFO,LogString)
                if ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.LOW)
                        t_end = time.time() + 13
                        while time.time() < t_end:
				DataWrite()
                        GPIO.output(5, GPIO.HIGH)
                        DataWrite()
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.HIGH)
                        t_end = time.time() + 13
                        while time.time() < t_end:
				DataWrite()
                        GPIO.output(5, GPIO.HIGH)
			DataWrite()
			
def Display():
        global Sensor
        global VBed1
        global VBed2
	global avg24h
	global avg5min
        now = datetime.now()
        T = now.strftime("%d-%m-%Y %H:%M:%S")
        LStatus = GPIO.input(12)
        PStatus = GPIO.input(21)
        FStatus = GPIO.input(20)
        ValveD = GPIO.input(6)

        Shed = dbRead('Shed')
        mode = Shed[1]
        period = Shed[2]
        LastFlood = Shed[3]
        NextFlood = Shed[4]
        H2O = dbRead('H2O')
        date=H2O[0]
        temp=H2O[1]
        pH = H2O[2]
        EC = H2O[3]
        TDS = H2O[4]
        S = H2O[5]
        SG = H2O[6]     

        Vol=dbRead('VolDrain')
        VolBed1 = Vol[9]
        VolBed2 = Vol[10]
        if LStatus:
                Lstatus = "On"
        else:
                Lstatus = "Off"
        if PStatus:
                Pstatus = "On"
        else:
                Pstatus = "Off"
        if FStatus:
                Fstatus = "On"
        else:
                Fstatus = "Off"
        if ValveD:
                ValveD = "bed 1"
        else:
                ValveD = "bed 0"
        try:
                if not Sensor:
                        Sensor = " "
        except:
               Sensor = " "
        try:
        	crp,phm,crp2 = Atlas(102,"D,?").split(',')
        	phm = float (float(phm) /1.0)
        except:
		phm = "0"
	try:
		crp,phpTV,crp2 = Atlas(102,"TV").split(',')
		phpTV = float (float(phpTV) /1.0)
        except:
                phpTV = 0

	try:	
		crp,php,crp2 = Atlas(101,"D,?").split(',')
        	php = float (float(php) /1.0)
        except: 
                php = "0"
	try:
                crp,phmTV,crp2 = Atlas(102,"TV").split(',')
                phmTV = float (float(phmTV) /1.0)
        except:
                phmTV = 0

	Deamonstat = os.system('systemctl is-active  growbot')
        if Deamonstat == 768 or Deamonstat == "inactive":
	        Deamonstat = "Deamon active"
                os.system('systemctl start growbot')
        elif Deamonstat == 0 or Deamonstat == "active":
                Deamonstat = "Deamon active"
	os.system('clear')
        print T, Sensor
        print "Daemon status: ", Deamonstat
	print ""
	print "Lights:\t",Lstatus, "\t\tTemp: ", ('%2.3f'%temp),"c\t\tpH: ", pH,  "\t\t    EC:",EC,"ppm"
        print "Pump:\t", Pstatus, "\t\tValve:\t",ValveD, "\t\t\t\t\t   TDS:", TDS,"ppm"
        print "Fan:\t", Fstatus, "\t\t\t\t\t\t\t\t     S:", S,"ppm"
        print "\t\t\t\t\t\t\t\t\t    SG:",SG
        print "" 
        print "\t\tmode:", mode, "   period:", period , "\t\t     Dispensed pH-/pH+:", phm,"(",phmTV,")/",php,"(",phpTV,")"
        print "\t\tLastFlood", LastFlood #, "\t\t Dispensed GrowA/GrowB: 0.00 / 0.00"
        print "\t\tNextFlood", NextFlood #, "\t\t   Dispensed FloA/FloB: 0.00 / 0.00"
        print ""
        print "\t\tBed 1: ", VolBed1,"L", " "
        print "\t\tBed 2: ", VolBed2,"L", " "
#	for thread in threading.enumerate(): 
#    		print(thread.name)                


def dbRead(table):
		try:
			Farm = mysql.connector.connect(
        	                        host="192.168.1.14",
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
		except:
			pass
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
					host="192.168.1.14",
					user="pi",
					passwd="a-51d41e",
					database="Farm"
			)

			SheD = Farm.cursor()
			# select * from farmdata order by date desc limit 1;
			# +---------------------+------+--------+-------+---------+-----------+------+------+
			# | date                | main | lights | ExFan | AirPump | WaterPump | 3wv  | 3wvD |
			# +---------------------+------+--------+-------+---------+-----------+------+------+
			# | 2020-03-21 15:39:09 | On   | On     | Off   | Off     | Off       | On   | Circ |
			# +---------------------+------+--------+-------+---------+-----------+------+------+
			sql = "insert INTO Farm.farmdata (date,main,lights,ExFan,AirPump,WaterPump,3wv,3wvD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			val = (Date, main, Lights, ExFan, APump, WPump, ValveS,ValveD)
			SheD.execute(sql, val)
			SheD.close
			Farm.commit()

def pHECT():
        global temp
        global pH
        global EC
        global TDS
        global S
        global SG
        global pHVar
        global ECVar
        GPIO.setmode(GPIO.BCM)
        while True:
                        now = datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
                        pH = Atlas(99,"r")
                        while pH == "Error 254" or pH == "Error 255" or pH == "?I,pH,1.96":
                                pH = Atlas(99,"r")
                        ECs = Atlas(100,"r")
                        while ECs == "Error 254" or ECs == "Error 255" or ECs == "?I,EC,2.12":
                                ECs = Atlas(100,"r")
                        ECs.split(',')
                        Ec,TDS,S,SG = ECs.split(',')
                        EC = float (float(Ec) /1.0)
                        TDS = float (float(TDS) / 1.0)
                        S = float (float(S) * 1000)
                        SG = float (float(SG) / 1.0)
                        ########
                        # Temp #
                        ########
			path = "/sys/bus/w1/devices/"
                        dir_list = os.listdir(path)
                        for path in dir_list:
                                if '28' in path:
                                        path = "/sys/bus/w1/devices/" + path + "/w1_slave"
                                        f = open(path, "r")
                                        for last_line in f:
                                                try:
                                                        temp = last_line.split()
                                                        temp = str(temp[-1])
                                                        temp = (float(temp.strip("t=")) /1000 )
                                                except:
                                                       pass
                        try:
				if temp > 45:
                                	temp = '28'
                        	if temp > 29.8 and temp < 45:
                                	GPIO.output(20, GPIO.HIGH)
                        	elif temp < 28.3  or temp > 50:
                                	GPIO.output(20, GPIO.LOW)
                        except:
				temp = '23.57'
			last=dbRead('H2O')
                        LDate = last[0]
                        date = datetime.now()
                        SinceLast = date-LDate
                        SinceLastSec = SinceLast.seconds
                        if SinceLastSec > 5:
			        Farm = mysql.connector.connect(
                                        host="192.168.1.14",
                                        user="pi",
                                        passwd="a-51d41e",
                                        database="Farm"
                                )
                                H2O = Farm.cursor()
                                sql = "INSERT INTO Farm.H2O (date,Temp,pH,EC,TDS,S,SG) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                val = (now,temp,pH,Ec,TDS,S,SG)
                                H2O.execute(sql, val)
                                H2O.close
                                Farm.commit()
                                Farm.close

def Calibrate():
	delais = 30
	while True:
		global avg24h
		global avg5min
		global pHdiff
		H2O=dbRead('H2O')
#		date = H2O[0]
                pH = H2O[2]
		EC = H2O[3]
		CAL=dbRead('Cal')
		date = CAL[0]
		now = datetime.now()
		SinceLast = now-date
		SinceLastMin = SinceLast.seconds / 60
		date = date.strftime("%Y-%m-%d %H:%M:%S")
		if (pH < 5.4 or pH > 5.6)  and SinceLastMin > 20:
			LogString="Cal thread:" + " " + str(pH) + " " + "Last Cal:" + " " + date
        	        LogString=str(LogString)
	                syslog.syslog(syslog.LOG_INFO,LogString)
			LogString="Cal thread: pre-cal checks"
	                LogString=str(LogString)
	                syslog.syslog(syslog.LOG_INFO,LogString)
		        Date = now.strftime("%Y-%m-%d %H:%M:%S")
                        Farm = mysql.connector.connect(
                                host="192.168.1.14",
                                user="pi",
                                passwd="a-51d41e",
                                database="Farm"
                        )
                        cursor = Farm.cursor()
                        cursor.execute("select (avg (pH)) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 5 MINUTE)")
                        myresult = cursor.fetchone()
                        avg5min = myresult[0] 
                        cursor.close 
                        try:
				avg5min = round(float(avg5min), 4)
			except:
				avg5min= "0"
			LogString="Cal thread: pH: " + str(pH) + " 5min avg:  " + str(avg5min) + " Last Cal: " + date
        	        LogString=str(LogString)
	                syslog.syslog(syslog.LOG_INFO,LogString)
			if (avg5min < 5.4 or avg5min > 5.6):
				LogString="Cal thread: Calibrating" 
        	                LogString=str(LogString)
	                        syslog.syslog(syslog.LOG_INFO,LogString)
				Cal=dbRead('Cal')
				date = Cal[0]
				pHDelta = Cal[1]
				ECDelta = Cal[2]
				DpHp = Cal[3]
				VpHp = Cal[4]
				DpHm = Cal[5]
				VpHm = Cal[6]
				DFloA = Cal[7]
				VFloA = Cal[8]
				DFloB = Cal[9]
				VFloB = Cal[10]
				DVegA = Cal[11]
				VVegA = Cal[12]
				DVegB = Cal[13]
				VVegB = Cal[14]
				pHdiff = round ((float(pH) -5.5),2)
				pHVol = round ((pHdiff * 0.5 * 100), 2)
				LogString="Cal thread: Calibrating for " + str(pHdiff) + " with " + str(pHVol)
       	                        LogString=str(LogString)
                                syslog.syslog(syslog.LOG_INFO,LogString)
				cursor = Farm.cursor()
				sql = "insert into Farm.Cal (date, pHDelta, ECDelta, DpHp, VpHp, DpHm, VpHm, DFloA, VFloA,  DFloB, VFloB, DVegA, VVegA, DVegB, VVegB) VALUES(%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
				if pHdiff > '0':
					phstr = "D," + str(pHVol) + ",2"
					#Atlas(102, phstr)
					LogString="Cal thread: Calibrated " + str(pHVol) +"mL of pH-"
       		                        LogString=str(LogString)
                	                syslog.syslog(syslog.LOG_INFO,LogString)
					pHmr = Atlas(102,"D,?")
		                        while pHmr == "Error 254" or pHmr == "Error 255" or pHmr == "?I,PMP,1.02":
                	                	pHmr = Atlas(102,"D,?")
                			        pHmr.split(',')
			                        crp,phm,crp2 = pHmr.split(',')
               				phm = float (float(phm) /1.0)
					val = (Date, pHdiff,ECDelta, DpHp, VpHp, Date, phm, DFloA, VFloA,  DFloB, VFloB, DVegA, VVegA, DVegB, VVegB)
				elif pHdiff < '0':
					pHVol = abs(pHVol)
					phstr = "D," + str(pHVol ) + ",2"
					#Atlas(101, phstr)
					LogString="Cal thread: Calibrated " + str(pHVol) +"mL of pH+"
                                        LogString=str(LogString)
                                        syslog.syslog(syslog.LOG_INFO,LogString)
					pHpr = Atlas(101,"D,?")
                                        while pHpr == "Error 254" or pHpr == "Error 255" or pHpr == "?I,PMP,1.02":
                                                pHpr = Atlas(102,"D,?")
                                        pHpr.split(',')
                                        crp,php,crp2 = pHpr.split(',')
                                       	php = float (float(php) /1.0)
					val = (Date, pHdiff,ECDelta, Date, pHVol, DpHm, VpHm, DFloA, VFloA,  DFloB, VFloB, DVegA, VVegA, DVegB, VVegB)
				delais = 300
				cursor.execute(sql, val)
				Farm.commit()
				cursor.close
				Farm.close
		else:
			LogString="Cal thread:" + " " + str(pH) + " " + "Last Cal:" + " " + date + " (" + str(SinceLastMin) + " min(" + str(delais) + "))"
	                LogString=str(LogString)
        	        syslog.syslog(syslog.LOG_INFO,LogString)
			time.sleep(delais)
			delais = delais + 10
class atlas_i2c:
                long_timeout = 1.5 # the timeout needed to query readings and calibrations
                short_timeout = .5 # timeout for regular commands
                default_bus = 1 # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
                default_address = 99 # the default address for the pH sensor
                def __init__(self, address=default_address, bus=default_bus):
                        # open two file streams, one for reading and one for writing
                        # the specific I2C channel is selected with bus it is usually 1, except for older revisions where its 0 wb and rb indicate binary read and write
                        self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
                        self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
                        # initializes I2C to either a user specified or default address
                        self.set_i2c_address(address)
                def set_i2c_address(self, addr):
                        # set the I2C communications to the slave specified by the address
                        0 # The commands for I2C dev using the ioctl functions are specified in
                        # the i2c-dev.h file from i2c-tools
                        I2C_SLAVE = 0x703
                        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
                        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
                def write(self, string):
                        # appends the null character and sends the string over I2C
                        string += "\00"
                        self.file_write.write(string)
                def read(self, num_of_bytes=31):
                        # reads a specified number of bytes from I2C, then parses and displays the result
                        res = self.file_read.read(num_of_bytes) # read from the board
                        response = filter(lambda x: x != '\x00', res) # remove the null characters to get the response
                        if (ord(response[0]) == 1): # if the response isnt an error
                                        char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:])) # change MSB to 0 for all received characters except the first and get a list of characters
                                        # NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
                                        return ''.join(char_list) # convert the char list to a string and returns it
                        else:
                                        return "Error " + str(ord(response[0]))
                def query(self, string):
                        # write a command to the board, wait the correct timeout, and read the response
                        self.write(string)
                        # the read and calibration commands require a longer timeout
                        if ((string.upper().startswith("R")) or
                                        (string.upper().startswith("CAL"))):
                                        time.sleep(self.long_timeout)
                        elif ((string.upper().startswith("SLEEP"))):
                                        return "sleep mode"
                        else:
                                        time.sleep(self.short_timeout)
                        return self.read()
                def close(self):
                        self.file_read.close()
                        self.file_write.close()

def Atlas(addr,verb):
                try:
                                device = atlas_i2c()  # creates the I2C port object, specify the address or bus if necessary
                                device.set_i2c_address(int(addr))
                                try:
                                                Type = device.query('i')[3:5]
                                                value = (device.query(verb))
                                except IOError:
                                                print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
                                return value
                except IOError:
                                print "No I2C port detected"
        
if __name__=="__main__":

        Main()
