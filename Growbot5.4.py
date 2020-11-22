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
Pump = 21
Valve = 5
VDir = 6
DrainBed1 = 22
DrainBed2 = 18
PumpBed1 = 24
PumpBed2 = 25
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
global flow1
global flow1b
global flow2
global flow2b
global flow3
global flow4
global Oflow1
global Oflow1b
global Oflow2
global Oflow2b
global Oflow3 
global Oflow4
global Sensor
global NextFlood
global pHUp
global pHDn
global GrowA
global GrowB
global FloA
global FloB
global temp
global pH
global EC
global TDS
global S
global SG
global LastFlood
global NextFlood
temp = 0
pH = 0
EC = 0
TDS = 0
S = 0
SG = 0
pHUp = 0
pHDn = 0
GrowA = 0
GrowB = 0
FloA = 0
FloB = 0
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
Oflow1 = 0
Oflow2 = 0
Oflow3 = 0
Oflow4 = 0
Oflow1 = 0
Oflow1b = 0
Oflow2 = 0
Oflow2b = 0
Oflow3 = 0
Oflow4 = 0
Sensor = 0
NextFlood = 0

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
                                "No I2C port detected"
#                return value

class ReadSensors(threading.Thread):
        def __init__(self, Read_Chem_Sensors):
                threading.Thread.__init__(self)
                self.runnable = Read_Chem_Sensors
        def run(self):
                self.runnable()

class Write_Hall(threading.Thread):
        def __init__(self, Write_Hall):
                threading.Thread.__init__(self)
                self.runnable = Write_Hall
        def run(self):
                self.runnable()


def pHECT():
	global temp
	global pH
	global EC
	global TDS
	global S
	global SG
#	ECs = 0
#	temp = 0  
	GPIO.setmode(GPIO.BCM)
	while True:
			now = datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
#                        pH = 0
                        pH = Atlas(99,"r")
                        while pH == "Error 254" or pH == "Error 255":
                                pH = Atlas(99,"r")
#                        ECs = 0 
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
                        if temp > 45:
                                temp = '28'
                        if temp > 29.8 and temp < 45:
                                GPIO.output(20, GPIO.HIGH)
                        elif temp < 28.3  or temp > 50:
                                GPIO.output(20, GPIO.LOW)
			last=dbRead('H2O')
                	LDate = last[0]
			date = datetime.now()
			SinceLast = date-LDate
	                SinceLastSec = SinceLast.seconds
        	        if SinceLastSec > 5:
                	        Farm = mysql.connector.connect(
                        	        host="localhost",
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
				DataWrite()
				Calibrate(pH,ECs)

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
	PStatus = GPIO.input(21)
	ValveD = GPIO.input(6)
	Farm = mysql.connector.connect(
		host="localhost",
		user="pi",
		passwd="a-51d41e",
		database="Farm"
	)
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
	if (channel == DrainBed1):
			Sensor = "Drain 1"
			count1 = count1 + 1
			count3 = count3 - 1.6
			flow1 = round((count1 / (60 * 28.3906)),3)
			flow3 = round((count3 / (60 * 28.3906)),3)
	if (channel == DrainBed2):
			Sensor = "Drain 2"
		        count2 = count2 + 1
			count4 = count4 - 1.1
			flow2 = round(count2 / (60 * 28.3906),3)
			flow4 = round(count4 / (60 * 28.3906),3)
	if PStatus and not ValveD and (channel == PumpBed1):
			Sensor = "Pump 1"
		        count3 = count3 + 1.5
			flow3 = round(count3 / (60 * 28.3906),3)
        if PStatus and ValveD and (channel == PumpBed2):
			Sensor = "Pump 2"
		        count4 = count4 + 1
			flow4 = round(count4 / (60 * 28.3906),3)
	if flow3 <= 0:
		flow3 = 0
	if flow4 <= 0:
                flow4 = 0

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
                                Display()
				HallWrite()
                        GPIO.output(5, GPIO.HIGH)
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.HIGH)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                Display()
				HallWrite()
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


def HallReset():
	while True: 
		date = datetime.now()
	        Date = date.strftime("%Y-%m-%d %H:%M:%S")
		Farm = mysql.connector.connect(
 	        	host="localhost",
                       	user="pi",
                       	passwd="a-51d41e",
                       	database="Farm"
                	)
                VolDrain = Farm.cursor()
		VolDrain.execute ("select now(),TIMESTAMPDIFF(SECOND, (select DH1 from VolDrain order by date desc limit 1), now()) as timediff_DH1, TIMESTAMPDIFF(SECOND, (select DH2 from VolDrain order by date desc limit 1), now()) as timediff_DH2, TIMESTAMPDIFF(SECOND, (select DH3 from VolDrain order by date desc limit 1), now()) as timediff_DH3, TIMESTAMPDIFF(SECOND, (select DH4 from VolDrain order by date desc limit 1), now()) as timediff_DH4;")
		myresult = VolDrain.fetchone()
#		try:
              	date = myresult[0]
		timediff_DH1 = myresult[1]
		timediff_DH2 = myresult[2]
		timediff_DH3 = myresult[3]
               	timediff_DH4 = myresult[4]
#		except TypeError:
#                      	        pass
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
		PStatus = GPIO.input(21)
		VD = Farm.cursor()
#		print "PStatus:",PStatus
#		print "timediff_DH1:", h1, timediff_DH1
#		print "timediff_DH2:", h2, timediff_DH2
#		print "timediff_DH3:", h1, timediff_DH3
#		print "timediff_DH4:", h4, timediff_DH4

	        if not PStatus:
			sql = """UPDATE VolDrain SET date = %s, DH3 = %s, Hall3 = %s,  DH4 = %s, Hall4 = %s  where date = (select date from VolDrain order by date desc limit 1)"""
        	        data = (Date, Date, "0", Date, "0")
			VD.execute(sql, data)
                        VD.close 
                        Farm.commit()
			flow3 = 0
			flow4 = 0
#			print "reset Pump"
		if  h1 and timediff_DH1 > 2:
			flow3 = "0"
			sql = """UPDATE VolDrain SET date = %s, DH1 = %s, Hall1 = %s, VolBed1 = %s where date = (select date from VolDrain order by date desc limit 1)"""
			data = (Date, Date, "0", "0")
			VD.execute(sql, data)
			VD.close
        		Farm.commit()
#			print "reset dain1"
               	if h2 and timediff_DH2 > 2:
			flow4 = "0"
               	       	sql = """UPDATE VolDrain SET date = %s, DH2 = %s, Hall2 = %s, VolBed2 = %s where date = (select date from VolDrain order by date desc limit 1)"""
               		data = (Date, Date, "0", "0")
                       	VD.execute(sql, data)
       	               	VD.close
               	       	Farm.commit()
#			print "reset dain2"
               	if h3 and timediff_DH3 > 1 :
       	               	sql = """UPDATE VolDrain SET date = %s, DH3 = %s, Hall3 = %s where date = (select date from VolDrain order by date desc limit 1)"""
               	       	data = (Date, Date, "0")
              		VD.execute(sql, data)
                       	VD.close
       	               	Farm.commit()
#			print "reset bed1+"
      		if h4 and timediff_DH4 > 1:
              		sql = """UPDATE VolDrain SET date = %s, DH4 = %s, Hall4 = %s where date = (select date from VolDrain order by date desc limit 1)"""
                       	data = (Date, Date, "0")
			VD.execute(sql, data)
       		       	VD.close
               		Farm.commit()
#			print "reset bed2+"
def Display():
	now = datetime.now()
        T = now.strftime("%d-%m-%Y %H:%M:%S")
	LStatus = GPIO.input(12)
	PStatus = GPIO.input(21)
	FStatus = GPIO.input(20)
	Shed=dbRead('Shed')
	LastFlood =Shed[3]
	NextFlood = Shed[4]
	H2O=dbRead('H2O')
	date = H2O[0]
        temp = H2O[1]
        pH = H2O[2]
        EC = H2O[3]
        TDS = H2O[4]
        S = H2O[5]
        SG = H2O[6]	
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
	os.system('clear')
        print T
	print ""
	try:
	        print "Lights:\t",Lstatus, "\t Temp: ", ('%2.3f' %temp),"c\t\tpH: ", pH, "\t EC: ", EC,"ppm"
	except:
		pass
	print "Pump:\t", Pstatus, "\t\t\t\t\t\t\t TDS:", TDS,"ppm"
	print "Fan:\t", Fstatus, "\t\t\t\t\t\t\t S  :", S,"ppm"
	print "\t\t\t\t\t\t\t\t SG:  ",SG
        print "" 
        print "\t   LastFlood", LastFlood, "\t\tDispensed pH-/pH+\t", pHDn,"/",pHUp
	print "\t   NextFlood", NextFlood, "\t\tDispensed GrowA/GrowB\t0.00 / 0.00" #, GrowA,"/",GrowB
	print "\t\t\t\t\t\t\tDispensed FloA/FloB\t0.00 / 0.00"
        print ""
        print "\t\tPump Bed1 Volume: ", flow3,"L"
        print "\t\tPump Bed2 Volume: ", flow4,"L"

def HallWrite():
	global flow3 
        global flow4
	global Oflow3 
	global Oflow4
	if Oflow3 <= 0:
		Oflow3 = 0
        if Oflow4 <= 0:
                Oflow4 = 0
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
       	Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
	DV = Farm.cursor()
	now = datetime.now()
        Date = now.strftime("%Y-%m-%d %H:%M:%S")
	PStatus = GPIO.input(21)
	sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
	if Oflow3 != flow3:
		if Oflow3 > flow3:
			data = (Date, Date, "1", HD2, h2, HD3, h3, HD4, h4, flow3, flow4)
		else:
                        data = (Date, HD1,h1, HD2, h2, Date, "1", HD4, "0", flow3, flow4)
	if Oflow4 != flow4:
		if Oflow4 > flow4:
			data = (Date, HD1,h1,Date, "1", HD3, h3, HD4, h4, flow3, flow4)
		else:
			data = (Date, HD1,h1, HD2, h2, HD3, "0", Date, "1", flow3, flow4)
        try:
                DV.execute(sql, data)
                DV.close
                Farm.commit()
        except:
                pass
        Oflow3 = flow3 
        Oflow4 = flow4
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
                DayEnd = "18:00:00"
	else:
		mode = "Vegetative"
                DayStart = "06:00:00"
                DayEnd = "22:00:00"

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
	PStatus = GPIO.input(21)
	ValveD = GPIO.input(6)
	now = datetime.now()
	Date = now.strftime("%Y-%m-%d %H:%M:%S")
	Shed=dbRead('Shed')
	try:
		period = Shed[2]
		LastFlood = Shed[3]
        	NextFlood = Shed[4]
		SinceLast = now-LastFlood
		SinceLastMin = SinceLast.seconds / 60
	except:
		period =  "24"
		NextFlood = now
		LastFlood = (now - DT.timedelta(days = 1))
		SinceLast = now-LastFlood
		SinceLastMin = "31"
	if now >= NextFlood:
		print LastFlood, NextFlood,"2", flow1, flow2
		time.sleep(2)
		if not PStatus  and flow1 == 0 and flow2 == 0:
			Valve(0)
			GPIO.output(26, GPIO.HIGH)
		        GPIO.output(21, GPIO.HIGH)
			DataWrite()
		value = ""
		Display()
		if ValveD and flow2 > 0.075:
                        GPIO.output(21, GPIO.LOW)
                        HallWrite()
                        if SinceLastMin > 30:
                                DataWrite()
                                now = datetime.now()
                                NextFlood = now + DT.timedelta(hours = int(period))
                                Farm = mysql.connector.connect(
                                        host="localhost",
                                        user="pi",
                                        passwd="a-51d41e",
                                        database="Farm"
                                )
                                SheD = Farm.cursor(prepared=True)
                                sql = """UPDATE Shed SET date = %s, NextFlood = %s where date = (select date from Shed order by date desc limit 1)"""
                                data = (now,NextFlood)
                                SheD.execute(sql,data)
                                SheD.close
                                Farm.commit()

		elif flow1 > 0.12 and not ValveD:
			#print flow1
			GPIO.output(21, GPIO.LOW)
			while flow1 < (flow3 / 6):
				Display()
				HallWrite()
			Valve(1)
			GPIO.output(21, GPIO.HIGH)
			DataWrite()
		else:
			HallWrite()
	return LastFlood, NextFlood


def Calibrate(pH,ECs):
	global pHUp
	global pHDn
	ECs.split(',')
        Ec,TDS,S,SG = ECs.split(',')
        EC = float (float(Ec) /1.0)
        TDS = float (float(TDS) / 1.0)
        S = float (float(S) * 1000)
        SG = float (float(SG) / 1.0)
	if pH < 5:
		pHUp = Atlas(102,"D,?")
		pHUp = pHUp[+3:-2]
	elif pH > 6:
		pHDn = Atlas(101,"D,?")
		pHDn = pHDn[+3:-2]
	if EC < 2000:
		GrowA = Atlas(103,"D,?")
		GrowB = Atlas(104,"D,?")
		print Ec, "Dispenced A", GrowA, "Dispenced B", GrowB
		print Ec, "Need Feed"
	elif EC > 3000:
	        print Ec, "Need flat water"
        pHDn = Atlas(101,"D,?")
        pHDn = pHDn[+3:-2]
        pHUp = Atlas(102,"D,?")
        pHUp = pHUp[+3:-2]
#       GrowA = Atlas(103,"D,?")
#       GrowA = GrowA[+3:-2]
#       GrowB = Atlas(104,"D,?")     
#       GrowB = GrowB[+3:-2]
#       FloA = Atlas(105,"D,?")
#       FloA = FloA[+3:-2]
#       FloB = Atlas(106,"D,?") 
#       FloB = FloB[+3:-2]

#	"select ((MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 5 MINUTE);"
#	"select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 5 MINUTE);"
	
#	"select ((MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 30 MINUTE);"
#        "select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 30 MINUTE);"

#	"select (MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 2 HOUR );"
#        "select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 2 HOUR );"



def Main():
	global action
	try:
		option = sys.argv[1]
	except:
		option = "a"
	thread = ReadSensors(pHECT)
	thread2 = Write_Hall(HallReset)
	Deamonstat = os.system('systemctl is-active  growbot')
#	Deamonstat = os.system('service growbot status')
	if Deamonstat == 768 or Deamonstat == "inactive":
		Deamonstat = "UserLand"
		os.system('systemctl start growbot')
	elif Deamonstat == 0 or Deamonstat == "active":
		Deamonstat = "Deamon"
	else:
		Deamonstat = Deamonstat
	context=getpass.getuser()
	while True:
		if context == "root":
			Sensor = ""
	    		try:
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
                	                print "Running Hall watcher task"
                        	        thread2 = Write_Hall(HallReset) 
                                	thread2.setDaemon(False) #True)
	                                thread2.start()
        	                else:
                	                threadStat2 = "running"
                        	try:
					GPIO.add_event_detect(DrainBed1, GPIO.FALLING, callback=countPulse)
	                        except:
        	                        pass
                	        try:
					GPIO.add_event_detect(DrainBed2, GPIO.RISING, callback=countPulse)
	                        except:	
        	                        pass
                	        try:
					GPIO.add_event_detect(PumpBed1, GPIO.FALLING, callback=countPulse)
	                        except:
        	                        pass
                	        try:
					GPIO.add_event_detect(PumpBed2, GPIO.FALLING, callback=countPulse)
	                        except:
        	                        pass

				LStatus = GPIO.input(12)
		        	PStatus = GPIO.input(21)
				FStatus = GPIO.input(20)
    				Light()
				Flood()
				HallWrite()
				
				try:
					LogString="Deamonstat",Deamonstat,"Lstatus", LStatus,"Pstatus", PStatus,"FStatus", FStatus,"temp", temp,"LastFlood", LastFlood,"NextFlood", NextFlood,"flow3", flow3,"flow4", flow4,"pH", pH,"EC", EC,"S", S,"SG", SG,"pHDn", pHDn,"pHUp", pHUp,"GrowA", GrowA,"GrowB", GrowB,"FloA", FloA,"FloB", FloB
					LogString=str(LogString)
					syslog.syslog(syslog.LOG_INFO,LogString)
				except NameError:
					pass
	    		except KeyboardInterrupt:
	        		print '\ncaught keyboard interrupt!, bye'
        			GPIO.cleanup()
        			sys.exit()
	        if context == "pi":
			Display()
if __name__=="__main__":

        Main()
