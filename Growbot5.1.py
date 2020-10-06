#!/usr/bin/python
import os
import sys
import io
import fcntl
import time
import datetime
import RPi.GPIO as GPIO
import mysql.connector
import threading
GPIO.setmode(GPIO.BCM)
Pump = 21
Valve = 5
VDir = 6
DrainBed1 = 22
DrainBed2 = 18
PumpBed1 = 24
PumpBed2 = 25
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(12 , GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
global count1
global count2
global count3
global count4
global flow1
global flow2
global flow3
global flow4
global Sensor
global HD1
global Hall1
global HD2
global Hall2
global HD3
global Hall3
global HD4
global Hall4
global VolBed1
global VolBed2
count1 = 0
count2 = 0
count3 = 0
count4 = 0
flow1 = 0
flow2 = 0
flow3 = 0
flow4 = 0
HD1 = 0
HD2 = 0
VolBed1 = 0
VolBed2 = 0
HD3 = 0
HD4 = 0
Hall1 = 0
Hall2 = 0
Hall3 = 0
Hall4 = 0

Drain1 = 22
Drain2 = 18
PBed1 = 24
PBed2 = 25
GPIO.setup(Drain1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Drain2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PBed1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PBed2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)


############################################################################
def main():
  try:
    # Loop until users quits with CTRL-C
    thread = ChemSensors(ReadSensors)
    while True :
	if thread.is_alive() is False:
		thread = ChemSensors(ReadSensors)
		thread.start()
	try:
		GPIO.add_event_detect(22, GPIO.FALLING, callback=HallSensor)
        except:
                pass
        try:
		GPIO.add_event_detect(18, GPIO.FALLING, callback=HallSensor)
        except:
                pass
        try:
		GPIO.add_event_detect(24, GPIO.FALLING, callback=HallSensor)
        except:
                pass
        try:
		GPIO.add_event_detect(25, GPIO.FALLING, callback=HallSensor)
        except:
                pass
	Light()
	Flood()
	time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()
    sys.exit(0)
###############################
def truncate(n, decimals=0):
    multiplier = 1 ** decimals
    return int(n * multiplier) / multiplier
################################################################

def HallSensor(channel):
#       global T
#       T = 0
        global count1
        global count2
        global count3
        global count4
        global flow1
        global flow2
        global flow3
        global flow4
        global Sensor
	global HD1
	global Hall1
	global HD2
	global Hall2
	global HD3
	global Hall3
	global HD4
	global Hall4
	global VolBed1
	global VolBed2
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
#       now = datetime.now()
#       T = now.strftime("%H:%M:%S")
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
        if (channel == 22):
                        Sensor = "Drain1"
                        count1 = count1 + 1
			if VolBed1 > 1:
	                        count3 = count3 - 1
			else:
				VolBed1 = 0
        		VolBed1 = round(count3 * 9 / 60,5)
	                val = (now, now, "1", HD2, Hall2, HD3, Hall3, HD4, Hall4, VolBed1, VolBed2)
			print now, Sensor, count1, VolBed1
        if (channel == 18):
                        Sensor = "Drain2"
                        count2 = count2 + 1
			if VolBed2 > 0:
	                        count4 = count4 - 1
			else:
				VolBed2 = 0
                        VolBed2 = round(count4 * 9 / 60,5)
	                val = (now, HD1, Hall1, now, "1", HD3, Hall3, HD4, Hall4, VolBed1, VolBed2)
			print now, Sensor, count2, VolBed2
        if (channel == 24):
                        Sensor = "Pump1"
                        count3 = count3 + 1
                        VolBed1 = round(count3 * 9 / 60,5)
	                val = (now, HD1, Hall1, HD2, Hall2, now, "1", now, "0", VolBed1, VolBed2)
			print now, Sensor, count3, VolBed1
        if (channel == 25):
                        Sensor = "Pump2"
                        count4 = count4 + 1
                        VolBed2 = round(count4 * 9 / 60,5)
			val = (now, HD1, Hall1, HD2, Hall2, now , "0", now, "1", VolBed1, VolBed2)
			print now, Sensor, count4, VolBed1
        DV.execute(sql, val)
        DV.close
        Farm.commit()
#########################################################################
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
#############################################################################
def Atlas(addr,verb):
        try:
                device = atlas_i2c()  # creates the I2C port object, specify the address or bus if necessary
                device.set_i2c_address(int(addr))
                try:
                        Type = device.query('i')[3:5]
                        value = (device.query(verb))
                except IOError:
                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
        except IOError:
                "No I2C port detected"
        return value
########################################################################
class ChemSensors(threading.Thread):

    def __init__(self, Read_Chem_Sensors):
        threading.Thread.__init__(self)
        self.runnable = Read_Chem_Sensors

    def run(self):
        self.runnable()
#########################################################################
def ReadSensors():
	GPIO.setmode(GPIO.BCM)
	try:	
	        while True:
	                pHECT()
        	        DrainPump()
	except KeyboardInterrupt:
		# Reset GPIO settings
    		GPIO.cleanup()
    		sys.exit(0)
############################################################################
def pHECT():
		GPIO.setmode(GPIO.BCM)
		now = datetime.datetime.now()
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
#######################################################################################################################
def DrainPump():
		GPIO.setmode(GPIO.BCM)
		now = datetime.datetime.now()
		Farm = mysql.connector.connect(
                        host="localhost",
                        user="pi",
                        passwd="a-51d41e",
                        database="Farm"
                )
		DVcursor = Farm.cursor()
		DVcursor.execute("select DH1 from VolDrain where Hall1 = '1' order by date desc limit 1;")
		H1Date = DVcursor.fetchone()

		DVcursor = Farm.cursor()
		DVcursor.execute("select DH2 from VolDrain where Hall2 = '1' order by date desc limit 1;")
		H2Date = DVcursor.fetchone()

		DVcursor = Farm.cursor()
		DVcursor.execute("select DH3 from VolDrain where Hall3 = '1' order by date desc limit 1;")
		P1Date = DVcursor.fetchone()

		DVcursor = Farm.cursor()
		DVcursor.execute("select DH4 from VolDrain where Hall4 = '1' order by date desc limit 1;")
		P2Date = DVcursor.fetchone()
		DVcursor.close
		H1Date = str(''.join(map(str, H1Date)))
		H2Date = str(''.join(map(str, H2Date)))
		P1Date = str(''.join(map(str, P1Date)))
		P2Date = str(''.join(map(str, P2Date)))
		H1Date = datetime.datetime.strptime(H1Date,"%Y-%m-%d %H:%M:%S")
		H2Date = datetime.datetime.strptime(H2Date,"%Y-%m-%d %H:%M:%S")
		P1Date = datetime.datetime.strptime(P1Date,"%Y-%m-%d %H:%M:%S")
		P2Date = datetime.datetime.strptime(P2Date,"%Y-%m-%d %H:%M:%S")
		SinceLast1 = now-H1Date
		SinceLast2 = now-H2Date
         	PSinceLast1 = now-P1Date
        	PSinceLast2 = now-P2Date
		SinceLast1 = SinceLast1.seconds
                SinceLast2 = SinceLast2.seconds
		PSinceLast1 = PSinceLast1.seconds
		PSinceLast2 = PSinceLast2.seconds
		value = ""
		now = datetime.datetime.now()
	        T = now.strftime("%H:%M:%S")
	        now = now.strftime("%Y-%m-%d %H:%M:%S")
		Sensor = ""
     		if SinceLast1 > 2:
		        DV = Farm.cursor(prepared=True)
			sql = """UPDATE VolDrain SET DH1 = %s, Hall1 = %s, VolBed1 = %s where date = (select date from VolDrain order by date desc limit 1)"""
			data =  (now, "0", "0")
			DV.execute(sql,data)
			DV.close

     		if SinceLast2 > 2:
			DV = Farm.cursor(prepared=True)
			sql = """UPDATE VolDrain SET DH2 = %s, Hall2 = %s, VolBed2 = %s where date = (select date from VolDrain order by date desc limit 1)"""
			data = (now, "0", "0")
			DV.execute(sql,data)
			DV.close

                if PSinceLast1 > 2:
                        DV = Farm.cursor(prepared=True)
			sql = """UPDATE VolDrain SET DH3 = %s, Hall3 = %s where date = (select date from VolDrain order by date desc limit 1)"""
                        data = (now, "0")
			DV.execute(sql,data)
                        DV.close

                if PSinceLast2 > 2:
                        DV = Farm.cursor(prepared=True)
			sql = """UPDATE VolDrain SET DH4 = %s, Hall4 = %s where date = (select date from VolDrain order by date desc limit 1)"""
                        data = (now, "0")
			DV.execute(sql,data)
                        DV.close
		Farm.commit()
#		print "P1:", PSinceLast1, "P2:", PSinceLast2
#		print "D1:", SinceLast1, "D2:", SinceLast2
		DVcursor = Farm.cursor()
		DVcursor.execute("select sum(Hall1) FROM (select date, Hall1 from VolDrain ORDER BY date desc limit 10) t;")
		Hall1 = DVcursor.fetchone()
		DVcursor.execute("select sum(Hall2) FROM (select date, Hall2 from VolDrain ORDER BY date desc limit 10) t;")
		Hall2 = DVcursor.fetchone()
                DVcursor.execute("select sum(Hall3) FROM (select date, Hall3 from VolDrain ORDER BY date desc limit 10) t;")
                Hall3 = DVcursor.fetchone()
                DVcursor.execute("select sum(Hall4) FROM (select date, Hall4 from VolDrain ORDER BY date desc limit 10) t;")
                Hall4 = DVcursor.fetchone()
		Hall1 = int(''.join(map(str, Hall1)))
		Hall2 = int(''.join(map(str, Hall2)))
		Hall3 = int(''.join(map(str, Hall3)))
                Hall4 = int(''.join(map(str, Hall4)))
		PStatus = GPIO.input(21)
		SinceLast = 0
                Shed=dbRead('Shed')
                mode =  Shed[1]
                period = Shed[2]
                LastFlood = Shed[3]
                now = datetime.datetime.now()
                NextFlood = now + datetime.timedelta(hours = int(period))
                SinceLast = now-LastFlood
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                SinceLastMin = SinceLast.seconds / 60
                now = datetime.datetime.now()
		if Hall1 == 10 and Hall2 < 10 and Hall3 == 10 :
			Valve("1")
			if SinceLastMin > 30:
                                SheD = Farm.cursor()
                                sql = "INSERT INTO Farm.Shed (date,mode,period,LastFlood,NextFlood) VALUES (%s, %s, %s, %s, %s)"
                                val = (now,mode,period,now,NextFlood)
                                SheD.execute(sql, val)
                                SheD.close
				 DV = Farm.cursor(prepared=True)
                        	sql = """UPDATE VolDrain SET DH3 = %s, Hall3 = %s where date = (select date from VolDrain order by date desc limit 1)"""
                        	data = (now, "0")
                        	DV.execute(sql,data)
                                Farm.commit()
		elif Hall2 == 10 and Hall4 == 10:
			GPIO.output(21, GPIO.LOW)
			if SinceLastMin > 30:
            			GPIO.output(21, GPIO.LOW)
		                SheD = Farm.cursor()
                                sql = "INSERT INTO Farm.Shed (date,mode,period,LastFlood,NextFlood) VALUES (%s, %s, %s, %s, %s)"
                                val = (now,mode,period,now,NextFlood)
                                SheD.execute(sql, val)
                                SheD.close
				DV = Farm.cursor(prepared=True)
                        	sql = """UPDATE VolDrain SET DH4 = %s, Hall4 = %s where date = (select date from VolDrain order by date desc limit 1)"""
                        	data = (now, "0")
                        	DV.execute(sql,data)
                        	DV.close
                                Farm.commit()
###########################################################################################################
def Light():
	Shed=dbRead('Shed')
	mode = Shed[1]
	now = datetime.datetime.now()
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
		DataWrite()
        else:
               	GPIO.output(12, GPIO.LOW)
		DataWrite()
	LStatus = GPIO.input(12)
#########################################################################
def Flood():
	Date = datetime.datetime.now()
	Date = Date.strftime("%Y-%m-%d %H:%M:%S")
	Act=dbRead('Data')
      	Hall = Act[8]
	Shed=dbRead('Shed')
       	NextFlood = Shed[4]
	PStatus = GPIO.input(21)
	Date = datetime.datetime.strptime(Date, '%Y-%m-%d  %H:%M:%S')
	if Date > NextFlood and not PStatus:
		print "in pump loop" 
		ValveD = GPIO.input(6)
		if ValveD and not PStatus:
			Valve("0")
		GPIO.output(26, GPIO.HIGH)
		GPIO.output(21, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
		DataWrite()
#############################################################
def Valve(dir):
	now = datetime.datetime.now()
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
#################################################################################################
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
###################################################################################################
def DataWrite():
        Date = datetime.datetime.now()
        Date = Date.strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")
	
        main = GPIO.input(26)
        Lights = GPIO.input(12)
	APump = GPIO.input(16)
        ExFan = GPIO.input(20)
        WPump = GPIO.input(21)
        ValveS = GPIO.input(5)
        ValveD = GPIO.input(6)
        #Act=dbDataRead()
        Act=dbRead('Data')
        LDate = Act[0]
        Lmain = Act[1]
        Llight = Act[2]
        LExFan = Act[3]
        LAPump = Act[4]
        LWPump = Act[5]
        LValveS = Act[6]
        LValveD = Act[7]
        Hall = 0
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
        sql = "insert INTO Farm.farmdata (date,main,lights,ExFan,AirPump,WaterPump,3wv,3wvD,Hall) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (Date, main, Lights, ExFan, APump, WPump, ValveS,ValveD,Hall)
        SheD.execute(sql, val)
        Farm.commit()


if __name__=="__main__":
   
   main()

