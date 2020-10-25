#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import sys
import os
import datetime as DT
from datetime import datetime
import math
import mysql.connector
import threading
import io
import fcntl
Light = 12
APump = 16
Pump = 21
Valve = 5
VDir = 6
DrainBed1 = 22
DrainBed2 = 18
PumpBed1 = 24
PumpBed2 = 25
Main = 26
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DrainBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DrainBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(Main, GPIO.OUT)
GPIO.setup(Pump, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
global option
global T
global count1
global count2
global count3
global count4
global Oldflow1
global Oldflow1b
global Oldflow2
global Oldflow2b
global Oldflow3
global Oldflow4
global flow1
global flow1b
global flow2
global flow2b
global flow3
global flow4
global Sensor
global PStatus
global LStatus
global Bed
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
Oldflow1 = 0
Oldflow2 = 0
Oldflow3 = 0
Oldflow4 = 0
Bed = 0
try:
        option = sys.argv[1]
except:
        option = "0"

def main():
	try:
		thread = ReadSensors(pHECT)
		while True:
			now = datetime.now()
		        T = now.strftime("%H:%M:%S")
			if thread.is_alive() is False:
#        	        	print "starting Chemical sensors task"
	                	thread = ReadSensors(pHECT) 
				thread.start()
			try:
	        		GPIO.add_event_detect(DrainBed1, GPIO.FALLING, callback=HallSensor, bouncetime=400)
		        except:
        		        pass
	        	try:
        	        	GPIO.add_event_detect(DrainBed2, GPIO.FALLING, callback=HallSensor, bouncetime=400)
		        except:
        		        pass
	        	try:
        	        	GPIO.add_event_detect(PumpBed1, GPIO.FALLING, callback=HallSensor, bouncetime=400)
		        except:
        		        pass
	        	try:
        	        	GPIO.add_event_detect(PumpBed2, GPIO.FALLING, callback=HallSensor, bouncetime=400)
		        except:
        		        pass

			Light()
		        Flood()
			Display()
			DataWrite()
	except KeyboardInterrupt:
		print '\ncaught keyboard interrupt!, bye'
                GPIO.cleanup()
                sys.exit()
	

def Display():
        now = datetime.now()
        T = now.strftime("%H:%M:%S")
        os.system('clear')
	PStatus = GPIO.input(21)
        LStatus = GPIO.input(12)
	print T
	print ""
        print "Light: ",LStatus, "Pump: ", PStatus 
        print "Pump Bed1 Volume: ", flow3,"L"
        print "Drain Bed1 Volume: ", flow1,"L\t", flow1b,"L"
        print ""
        print "Pump Bed2 Volume: ", flow4,"L"
        print "Drain Bed2 Volume: ", flow2,"L\t", flow2b,"L"
        time.sleep(0.9)

def Light():
        Shed=dbRead('Shed')
        mode = Shed[1]
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        if mode == "Vegetative":
                DayStart = "06:00:00"
                DayEnd = "22:00:00"
        elif mode == "Flowering":
                DayStart = "08:00:00"
                DayEnd = "18:00:00"
        if now > DayStart  and  now < DayEnd:
                GPIO.output(26, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)
        else:
                GPIO.output(12, GPIO.LOW)
        LStatus = GPIO.input(12)

def Flood():
	Date = datetime.now()
	now = Date
	Date = Date.strftime("%Y-%m-%d %H:%M:%S")
	Date = datetime.strptime(Date, '%Y-%m-%d  %H:%M:%S')
	Shed=dbRead('Shed')
	period = Shed[2]
	LastFlood = Shed[3]
        NextFlood = Shed[4]
	PStatus = GPIO.input(21)
	SinceLast = now-LastFlood
	SinceLastMin = SinceLast.seconds / 60
	option = 0
	Bed = 0
	if Date > NextFlood  and PStatus == 0:
	        if not PStatus:
        	        PStatus == "Off"
	                print "Pump off, turning on"
        	        GPIO.output(26, GPIO.HIGH)
                	GPIO.output(21, GPIO.HIGH)
	                time.sleep(0.5)
        	        if Oldflow3 != flow3:
                	        print "Flood bed 1"
                        	Bed="0"
	        	elif Oldflow4 != flow4:
        	                print "Flood bed 2"
                	        Bed="1"
	                if option != Bed:
        	                GPIO.output(21, GPIO.LOW)
                	        Valve(option)
                        	GPIO.output(21, GPIO.HIGH)
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
	        if Oldflow1 != flow1:
        	        if option == 0:
                	        option = 1
                        	Valve("1")
	        if Oldflow2 != flow2:
        	        Valve("0")
                	GPIO.output(21, GPIO.LOW)
		

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

def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier

def countPulse(channel):
	GPIO.setwarnings(False)
	global count1
	global count2
	global count3
	global count4
	global Oldflow1
	global Oldflow1b
        global Oldflow2
        global Oldflow2b
        global Oldflow3
        global Oldflow4
        global flow1
        global flow1b
        global flow2
        global flow2b
        global flow3
        global flow4
	global Sensor
	global Bed
	global option
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
	VD=dbRead('VolDrain')
	date = VD[0]
	HD1 = VD[1]
	Hall1 = VD[2]
	HD2 = VD[3]
	Hall2 = VD[4]
	HD3 = VD[5]
	Hall3 = VD[6]
	HD4 = VD[7]
	Hall4 = VD[8]
	VolBed1 = VD[9]
	VolBed2 = VD[10]
	Farm = mysql.connector.connect(
		host="localhost",
		user="pi",
		passwd="a-51d41e",
		database="Farm"
	)
	now = datetime.datetime.now()
	now = now.strftime("%Y-%m-%d %H:%M:%S")
	DV = Farm.cursor()
	sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
	if (channel == DrainBed1):
			Sensor = "Drain 1"
			option = 1
			count1 = count1 + 1
			count3 = count3 - 1
			Oldflow1 = flow1
			Oldflow1b = flow1b
			flow1 = round((count1 / (60 * 28.3906)),3)
			flow1b = round((count3 / (60 * 28.3906)),3)
			val = (now, now, "1", HD2, Hall2, HD3, Hall3, HD4, Hall4, flow1b, VolBed2)
	if (channel == DrainBed2):
			Sensor = "Drain 2"
		        count2 = count2 + 1
			count4 = count4 - 1
			Oldflow2 = flow2
			Oldflow2b = flow2b
			flow2 = round(count2 / (60 * 28.3906),3)
			flow2b = round(count4 / (60 * 28.3906),3)
			val = (now, HD1, Hall1, now, "1", HD3, Hall3, HD4, Hall4, VolBed1, flow2b)
	if (channel == PumpBed1):
			Sensor = "Pump 1"
		        count3 = count3 + 1
			Oldflow3 = flow3
			flow3 = round(count3 / (60 * 28.3906),3)
			val = (now, HD1, Hall1, HD2, Hall2, now, "1", now, "0", flow3, VolBed2)
        if (channel == PumpBed2):
			Sensor = "Pump 2"
		        count4 = count4 + 1
			Oldflow4 = flow4
			flow4 = round(count4 / (60 * 28.3906),3)
			val = (now, HD1, Hall1, HD2, Hall2, now , "0", now, "1", VolBed1, flow4)
	DV.execute(sql, val)
	DV.close
	Farm.commit()
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
############################################################################
def pHECT():
        while True:
                try:
                        GPIO.setmode(GPIO.BCM)
                        now = datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
                        pH = 0
                        while pH == 0 or pH == "Error 254" or pH == "Error 255":
                                pH = Atlas(99,"r")
                        ECs = 0 
                        while ECs == 0 or ECs == "Error 254" or ECs == "Error 255" or ECs == "?I,EC,2.12":
                                ECs = Atlas(100,"r")
                        ECs.split(',')
                        Ec,TDS,S,SG = ECs.split(',')
                        Ec = float (float(Ec) /1.0)
                        TDS = float (float(TDS) / 1.0)
                        S = float (float(S) * 1000)
                        SG = float (float(SG) / 1.0)
                        ########
                        # Temp #
                        ########
                        path = "/sys/bus/w1/devices/"
                        dir_list = os.listdir(path)
                        temp = 0
                        while temp == 0 :
                                for path in dir_list:
                                        if '28' in path:
                                                path = "/sys/bus/w1/devices/" + path + "/w1_slave"
                                                f = open(path, "r")
                                                for last_line in f:
                                                        pass
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
                        elif temp < 28.3 or temp > 50:
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
                        	time.sleep(1)
			DataWrite()
                except KeyboardInterrupt:
                        # Reset GPIO settings
                        GPIO.cleanup()
                        sys.exit(0)


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
			# +---------------------+------+--------+-------+---------+-----------+------+------+------+
			# | date                | main | lights | ExFan | AirPump | WaterPump | 3wv  | 3wvD | Hall |
			# +---------------------+------+--------+-------+---------+-----------+------+------+------+
			# | 2020-03-21 15:39:09 | On   | On     | Off   | Off     | Off       | On   | Circ |  On  |
			# +---------------------+------+--------+-------+---------+-----------+------+------+------+
			sql = "insert INTO Farm.farmdata (date,main,lights,ExFan,AirPump,WaterPump,3wv,3wvD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			val = (Date, main, Lights, ExFan, APump, WPump, ValveS,ValveD)
			SheD.execute(sql, val)
			Farm.commit()
		hall=dbRead("VolDrain")
		h1=hall[2]
		h2=hall[4]
		h3=hall[6]
		h4=hall[8]
		if h1 or h2 or h3 or h4:
			LDate = hall[0]
			SinceLast = date-LDate
                        SinceLastSec = SinceLast.seconds
                        if SinceLastSec > 15:
				HD1=hall[1]
				HD2=hall[3]
				HD3=hall[5]
				HD4=hall[7]
	                        Farm = mysql.connector.connect(
        	                                host="localhost",
                	                        user="pi",
                                	        passwd="a-51d41e",
                        	                database="Farm"
                        	)
                                H2O = Farm.cursor()
				sql = "INSERT INTO Farm.VolDrain (date,DH1,Hall1,DH2,Hall2,DH3,Hall3,DH4,Hall4,VolBed1,VolBed2) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
				val = (date, HD1, "0", HD2, "0", HD3, "0", HD4, "0", "0", "0")
				H2O.execute(sql, val)
                        	Farm.commit()
if __name__=="__main__":

	main()
