#!/usr/bin/env python3
import time, sys, os
import datetime as DT
import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime
import serial
import math
import syslog
main = 26
Pump = 21
ValveS = 5
ValveD = 6
Valve2D = 7
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) 
GPIO.setup(main, GPIO.OUT)
GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(ValveS, GPIO.OUT)
GPIO.setup(ValveD, GPIO.OUT)
GPIO.setup(Valve2D, GPIO.OUT)

def Main():

	Flood()

def Flood():
	global LastFlood
	global NextFlood
	global period
	global Sensor
	global flow1
	global flow2
	global flow3
	global flow4
	PStatus = GPIO.input(21)
	ValveD = GPIO.input(6)
	now = datetime.now()
	Date = now.strftime("%Y-%m-%d %H:%M:%S")
	os.system('clear')
	Shed=dbRead('Shed')
	date = Shed[0]
	mode = Shed[1]
	period = Shed[2]
	LastFlood = Shed[3]
	NextFlood = Shed[4]
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
	flow4 = VD[10]
	Farm = mysql.connector.connect(
		host="192.168.1.14",
		user="pi",
		passwd="a-51d41e",
		database="Farm"
	)
	DV = Farm.cursor()
	now = datetime.now()
	#now = now.strftime("%Y-%m-%d %H:%M:%S")
	sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
	H1Stat = Valve("1s")
	H3Stat = Valve("3s")
	SinceLast = now-LastFlood
	if now >= NextFlood:
		VStatus = Valve("s")
		if VStatus != "V1-On" and VStatus != "V1-Off":
			VStatus = Valve("1")
			time.sleep(0.3)
			VStatus = Valve("s")
			Valve("1r")
			Valve("3r")
		Valve("0")
		while not isinstance(H3Stat, float):
			try:
				H3Stat = float(Valve("3s"))
			except ValueError:
				time.sleep(0.5)
		GPIO.output(26, GPIO.HIGH)
		GPIO.output(21, GPIO.HIGH)
		while H3Stat < 1:
			try:
				H1Stat = float(Valve("1s"))
			except:
				pass
			time.sleep(0.2)
			try:
				H3Stat = float(Valve("3s"))
			except:
				pass
			now = datetime.now()
			now = now.strftime("%Y-%m-%d %H:%M:%S")
			data = (now, HD1, "0", HD2, h2, now, "1", HD4, h4, H1Stat, flow4)
			if H1Stat > 0:
				DV.execute(sql, data)
				DV.close
				Farm.commit()
				LogString="Pump: Flooding Bed 0, Pump flow: " + str(H1Stat)
				LogString=str(LogString)
				syslog.syslog(syslog.LOG_INFO,LogString)
			time.sleep(0.7)
		GPIO.output(26, GPIO.HIGH)
		GPIO.output(21, GPIO.LOW)
		Valve("2")
		Valve("0")
		while not isinstance(H3Stat, float):
			try:
				H3Stat = float(Valve("3s"))
			except:
				time.sleep(1)
				H3Stat=""
		VD=dbRead('VolDrain')
		OVBed1 = VD[9]
		BedVol1 = H1Stat - H3Stat
		print (round(BedVol1,2), OVBed1)
		while  round(BedVol1,2) != OVBed1:
			now = datetime.now()
			now = now.strftime("%Y-%m-%d %H:%M:%S")
			VD=dbRead('VolDrain')
			OVBed1 = VD[9]
			H3Stat=""
			while not isinstance(H3Stat, float):
				try:
					H3Stat = float(Valve("3s"))
				except ValueError:
					time.sleep(0.5)
					H3Stat=""
			BedVol1 = H1Stat - H3Stat
			print (round(BedVol1,2), OVBed1)
			if BedVol1 == OVBed1:
				BedVol1 = 0
			sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
			data = (now, now, "1", HD2, h2, HD3, "0", HD4, h4, BedVol1, flow4)
			DV.execute(sql, data)
			Farm.commit()
			LogString="Pump: Draining Bed 0, : " + str(BedVol1) + str("/") + str(H1Stat)
			LogString=str(LogString)
			syslog.syslog(syslog.LOG_INFO,LogString)
			time.sleep(0.7)

		sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
		data = (now, now, "0", HD2, h2, HD3, "0", HD4, h4, "0", flow4)
		DV.execute(sql, data)
		DV.close
		Farm.commit()
		Valve("1r")
		Valve("3r")
		now = datetime.now()
		NextFlood = now + DT.timedelta(hours = int(period))
		now = now.strftime("%Y-%m-%d %H:%M:%S")
		SheD = Farm.cursor() 
		sql = "INSERT INTO Farm.Shed (date, mode, period, LastFlood, NextFlood) VALUES (%s, %s, %s, %s,%s)"
		data = (Date,mode,period,now,NextFlood)
		SheD.execute(sql,data)
		SheD.close
		Farm.commit()
		Farm.close
		Valve("1r")
		Valve("3r")

def Valve(dir):
	ser = serial.Serial(
        	port='/dev/ttyAMA0', 
	        baudrate = 115800,
        	parity=serial.PARITY_NONE,
	        stopbits=serial.STOPBITS_ONE,
        	bytesize=serial.EIGHTBITS,
	        timeout=1
	)
	SerStr = str("V") + str(dir) + str("\n")
	ser.write(SerStr.encode())
	time.sleep(0.2)
	value = ""
	while not value:
		try:
			value = str(ser.readline().strip())
			value = value.strip("'b'")
			if value == "VC" or value == "V1" or value == "V2" or value == "V3" or value == "V4":
				return (value)
			else:
				try:
					value=float(value)
				except:
					value=""
					time.sleep(0.01)
					print (value)
		
				return(value)
		except: # serial.serialutil.SerialException:
			ser.close()
			ser = serial.Serial(
				port='/dev/ttyAMA0', 
				baudrate = 115800,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout=1
			)
			value = str(ser.readline().strip())
			value = value.strip("'b'")

	ser.close()
	return str(value)

def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier



def dbRead(table):
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
			RH = myresult[2]
			pH = myresult[3]
			EC = myresult[4]
			TDS = myresult[5]
			S = myresult[6]
			SG = myresult[7]
			return date, Temp, RH, pH, EC, TDS, S, SG
		except TypeError:
			pass
	if table == "Shed":
		#cursor = Farm.cursor()
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


if __name__=="__main__":

        Main()

