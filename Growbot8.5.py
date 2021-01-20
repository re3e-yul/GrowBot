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
GPIO.setup(DrainBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DrainBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PumpBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(main, GPIO.OUT, initial=0)
GPIO.setup(Lights, GPIO.OUT, initial=0)
GPIO.setup(APump, GPIO.OUT, initial=0)
GPIO.setup(ExFan, GPIO.OUT, initial=0)
GPIO.setup(Pump, GPIO.OUT, initial=0)
GPIO.setup(ValveS, GPIO.OUT, initial=0)
GPIO.setup(ValveD, GPIO.OUT, initial=0)
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
Oflow3 = 0
Oflow4 = 0

def Main():
	thread = ReadSensors(pHECT)
	while True:
		if thread.is_alive() is False:
                        threadStat = "not running"
                        print "starting Chemical sensors task"
                        thread = ReadSensors(pHECT) 
                        thread.setDaemon(True)
                        thread.start()
                else:
                        threadStat = "running"
		try:
			GPIO.add_event_detect(DrainBed1, GPIO.BOTH, callback=countPulse)
		except:
			pass
		try:
			GPIO.add_event_detect(DrainBed2, GPIO.BOTH, callback=countPulse)
		except:
			pass
		try:
			GPIO.add_event_detect(PumpBed1, GPIO.BOTH, callback=countPulse)
		except:
			pass
		try:
			GPIO.add_event_detect(PumpBed2, GPIO.BOTH, callback=countPulse)	
		except:
			pass
		Light()
		Flood()
		Display()

class ReadSensors(threading.Thread):
        def __init__(self, Read_Chem_Sensors):
                threading.Thread.__init__(self)
                self.runnable = Read_Chem_Sensors
        def run(self):
                self.runnable()


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
        global Oflow3
        global Oflow4
	global Sensor
	VDir = GPIO.input(6)
	PStatus = GPIO.input(21)
#	now = datetime.now()
#	T = now.strftime("%H:%M:%S")
	if (channel == DrainBed1):
			Sensor = "Drain 1"
			count1 = count1 + 0.7
			#count3 = count3 - 1
			flow1 = round( count1 ,3)
			flow1 = round((count1 / 100),3)
			flow3 = round((count3 / 100),3)
	if (channel == DrainBed2):
			Sensor = "Drain 2"
		        count2 = count2 + 0.4
			#count4 = count4 - 1
			flow2 = round(count2 / 100,3)
			flow4 = round(count4 / 100,3)
	if (channel == PumpBed1) and VDir == 0 and PStatus == 1 :
			Sensor = "Pump 1"
		        count3 = count3 + 0.5
			flow3 = round(count3 / 100,3)
        if (channel == PumpBed2) and VDir == 1 and PStatus == 1:
			Sensor = "Pump 2"
		        count4 = count4 + 0.3
			flow4 = round(count4 / 100,3)

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
        	        host="192.168.1.13",
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
                DayEnd = "18:55:00"
        else:
                mode = "Vegetative"
                DayStart = "08:00:00"
                DayEnd = "19:00:00"

        if now > DayStart  and  now < DayEnd:
                if not LStatus:
                        GPIO.output(26, GPIO.HIGH)
                        GPIO.output(12, GPIO.HIGH)
                       
        else:
                if LStatus:
                        GPIO.output(12, GPIO.LOW)
                       


def Flood():
	global LastFlood
	global NextFlood
	global period
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
	if now >= NextFlood:
		Valve(0)
		while Sensor!= "Drain 1":
			Display()
			GPIO.output(26, GPIO.HIGH)
			GPIO.output(21, GPIO.HIGH)
		while  flow1 < (flow3 / 100):
			Display()
		Valve(1)
                while Sensor!= "Drain 2":
			Display()
			GPIO.output(26, GPIO.HIGH)
		        GPIO.output(21, GPIO.HIGH)
		while flow2 < (flow4 / 100):
			Display()
		GPIO.output(21, GPIO.LOW)
		now = datetime.now()
                NextFlood = now + DT.timedelta(hours = int(period))
                Farm = mysql.connector.connect(
                	host="192.168.1.13",
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
	flow1 == 0
	flow2 == 0
	flow3 == 0
	flow4 == 0
		
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
 #                               HallSensor()
                                Display()
                        GPIO.output(5, GPIO.HIGH)
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.HIGH)
                        t_end = time.time() + 13
                        while time.time() < t_end:
#                                HallSensor()
                                Display()
                        GPIO.output(5, GPIO.HIGH)

def Display():
        global Sensor
        global VBed1
        global VBed2
        now = datetime.now()
        T = now.strftime("%d-%m-%Y %H:%M:%S")
        LStatus = GPIO.input(12)
        PStatus = GPIO.input(21)
        FStatus = GPIO.input(20)
        ValveD = GPIO.input(6)
        Shed=dbRead('Shed')
        mode  =Shed[1]
        period =Shed[2]
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
        os.system('clear')
        print T, Sensor
        print ""
	print "Lights:\t",Lstatus, "\tTemp: ", ('%2.3f'%temp),"c\t\tpH: ", pH,  "\t\t    EC:",EC,"ppm"
        print "Pump:\t", Pstatus, "\tValve:\t",ValveD, "\t\t\t\t\t\t   TDS:", TDS,"ppm"
        print "Fan:\t", Fstatus, "\t\t\t\t\t\t\t\t     S:", S,"ppm"
        print "\t\t\t\t\t\t\t\t\t    SG:",SG
        print "" 
        print "\t\tmode:", mode, "   period:", period #, "\t\t     Dispensed pH-/pH+:", pHDn, "(",pHDnT,")", "/",pHUp ,"(",pHUpT,")"
        print "\t\tLastFlood", LastFlood #, "\t\t Dispensed GrowA/GrowB: 0.00 / 0.00"
        print "\t\tNextFlood", NextFlood #, "\t\t   Dispensed FloA/FloB: 0.00 / 0.00"
        print ""
        print "\t\tPump Bed1 VBed1,: ", flow1,"L / ",flow3,"L" #, VolBed1,"L"
        print "\t\tPump Bed2 VBed2,: ", flow2,"L / ",flow4,"L" #, VolBed2,"L"
                


def dbRead(table):
		Farm = mysql.connector.connect(
                                host="192.168.1.13",
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
				temp = '28'
			last=dbRead('H2O')
                        LDate = last[0]
                        date = datetime.now()
                        SinceLast = date-LDate
                        SinceLastSec = SinceLast.seconds
                        if SinceLastSec > 5:
			        Farm = mysql.connector.connect(
                                        host="192.168.1.13",
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
