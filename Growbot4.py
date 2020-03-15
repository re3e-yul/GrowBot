#!/usr/bin/env python
import threading
#from threading import Thread
import RPi.GPIO as GPIO
import time
import datetime
from datetime import datetime
import os
import sys
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import sys # used for system calls
import subprocess
import re
import mysql.connector
from time import gmtime, strftime

def init():
	os.system('clear')
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)							#, initial=GPIO.LOW) # AC Main
        GPIO.setup(21, GPIO.OUT) 							#, initial=GPIO.LOW) # AC Lighs
        GPIO.setup(12, GPIO.OUT) 							#, initial=GPIO.LOW) # AC WaterPump
        GPIO.setup(16, GPIO.OUT)                                                        #, initial=GPIO.LOW) # AC Fan
        GPIO.setup(20, GPIO.OUT)                                                        #, initial=GPIO.LOW) # AC Air pump
        GPIO.setup(5, GPIO.OUT)                                                        #, initial=GPIO.LOW) #  DC 3 way valve on/off
        GPIO.setup(6, GPIO.OUT)                                                        #, initial=GPIO.LOW) #  DC 3 way valve direction
  	GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)  				#, initiate Hall sensor
  	GPIO.add_event_detect(22, GPIO.BOTH, callback=sensorCallback, bouncetime=900)   #, on Hall call function
#	AtlasDetect()
	return "ok"

def sensorCallback(channel):
  	# Called if sensor output changes
  	global vol
  	global stat
  	timestamp = time.time()
  	stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
  	if GPIO.input(channel):
        	try:
                	vol = vol+1

        	except:
                	vol = 0
        	pass
  	else:
        	try:
                	vol = vol+1
        	except:
                	vol = 0
        	pass
	#  try:
	if vol != 0:
		GPIO.output(12, GPIO.LOW)

class atlas_i2c():
	long_timeout = 2.0  # the timeout needed to query readings and calibrations
	short_timeout = 1.0  # timeout for regular commands
	default_bus = 1  # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	default_address = 99  # the default address for the pH sensor
	current_addr = default_address

	def __init__(self, address=default_address, bus=default_bus):
		# open two file streams, one for reading and one for writing
		# the specific I2C channel is selected with bus it is usually 1, except for older revisions where its 0 wb and rb indicate binary read and write
		self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
		self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
		# initializes I2C to either a user specified or default address
		self.set_i2c_address(address)

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		0  # The commands for I2C dev using the ioctl functions are specified in
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
		res = self.file_read.read(num_of_bytes)  # read from the board
		response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
		if (ord(response[0]) == 1):  # if the response isnt an error
			char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[
																1:]))  # change MSB to 0 for all received characters except the first and get a list of characters
			# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
			return ''.join(char_list)  # convert the char list to a string and returns it
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

	def list_i2c_devices(self):
		prev_addr = self.current_addr  # save the current address so we can restore it after
		i2c_devices = []
		for i in range(0, 128):
			try:
				self.set_i2c_address(i)
				self.read()
				i2c_devices.append(i)
			except IOError:
				pass
		self.set_i2c_address(prev_addr)  # restore the address we were using
		return i2c_devices

def AtlasDetect():
	device = atlas_i2c()
	p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
	for i in range(0,9):
		line = str(p.stdout.readline())
                line = line[3:]
                for match in re.finditer("[0-9][0-9]", line):
                	Addr = int(match.group(), 16)
                        device.set_i2c_address(Addr)
                        verb = 'i'
                        try:
                        	print "Address: ",Addr, "\tInfo: ", (device.query(verb))[3:]
                        except IOError:
                        	print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")

def Atlas(addr,verb):
	try:
		device = atlas_i2c()  # creates the I2C port object, specify the address or bus if necessary
		device.set_i2c_address(int(addr))
		try:
			Type = device.query('i')[3:5]
			value = (device.query(verb))
		#	print(device.query(verb))
		except IOError:
			print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
	except IOError:
		"No I2C port detected"
	return value


class BackChemSensors(threading.Thread):

    def __init__(self, ChemSensors):
        threading.Thread.__init__(self)
        self.runnable = ReadSensors
        self.daemon = True

    def run(self):
        self.runnable()

def ReadSensors():
		global EC
		global pH
		while True:
			now = datetime.now()
			now = now.strftime("%Y-%m-%d %H:%M:%S")
			pH = Atlas(99,"R")
	        	ECs = Atlas(100,"r")
			ECs.split(',')
			Ec,TDS,S,SG = ECs.split(',')
			Ec = float (float(Ec) / 1000)
			TDS = float (float(TDS) / 1000)
			S = float (float(S) / 1)
			Farm = mysql.connector.connect(
                		host="localhost",
                		user="pi",
                		passwd="a-51d41e",
                		database="Farm"
        		)
#			+---------------------+-------+------+------+------+------+
#			| date                | pH    | EC   | TDS  | S    | SG   |
#			+---------------------+-------+------+------+------+------+
#			| 2019-12-20 09:56:04 | 6.800 |  100 |  100 |  100 |    1 |
#			+---------------------+-------+------+------+------+------+

			H2O = Farm.cursor()
			sql = "INSERT INTO Farm.H2O (date,pH,EC,TDS,S,SG) VALUES (%s, %s, %s, %s, %s, %s)"
			val = (now,pH,Ec,TDS,S,SG)
			H2O.execute(sql, val)
			Farm.commit()
			H2O.close
			Mstatus = GPIO.input(26) #main
			Lstatus = GPIO.input(21) #Lights
			Pstatus = GPIO.input(12) #water pump
			Fstatus = GPIO.input(16) #Fan
			Bstatus = GPIO.input(20) #air pump 
			Valve = GPIO.input(5)    #valve on/off
			Valved = GPIO.input(6) 	 #valve dir 
			
			if Mstatus:
                		Mstatus = "On"
        		else:
                		Pstatus = "Off"

                        if Lstatus:
                                Lstatus = "On"
                        else:
                                Lstatus = "Off"

                        if Pstatus:
                                Pstatus = "On"
                        else:
                                Pstatus = "Off"

                        if Fstatus:
                                Fstatus = "On"
                        else:
                                Fstatus = "Off"

                        if Bstatus:
                                Bstatus = "On"
                        else:
                                Bstatus = "Off"

			if Valve:
				Valve = "Off"
			else:
				Valve = "On"

                        if Valved:
                                Valved = "Feed"
                        else:
                                Valved = "Circ"
			Farm = mysql.connector.connect(
                                host="localhost",
                                user="pi",
                                passwd="a-51d41e",
                                database="Farm"
                        )
			ACT = Farm.cursor()
			sql = "INSERT INTO Farm.farmdata (date,main,lights,ExFan,AirPump,WaterPump,3wv,3wvD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			val = (now,Mstatus,Lstatus,Pstatus,Fstatus,Bstatus,Valve,Valved)
			ACT.execute(sql, val)
			Farm.commit()
			ACT.close
#		return now,pH,Ec,TDS,S,SG



def dbH2ORead():
        Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
        #global mycursor
        h2ocursor = Farm.cursor()
        h2ocursor.execute("select * from Farm.H2O ORDER BY date DESC LIMIT 1")
        myresult = h2ocursor.fetchone()
	h2ocursor.close
#+---------------------+-------+------+------+------+------+
#| date                | pH    | EC   | TDS  | S    | SG   |
#+---------------------+-------+------+------+------+------+
#| 2019-12-20 09:56:04 | 6.800 |  100 |  100 |  100 |    1 |
#+---------------------+-------+------+------+------+------+
	try:
	        date = myresult[0]
		pH = myresult[1]
		EC = myresult[2]
		TDS = myresult[3]
		S = myresult[4]
		SG = myresult[5]
		return date, pH, EC, TDS, S, SG
	except TypeError:
		print "no entry yet"

def dbShedRead():
        Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
        #global mycursor
        SheDcursor = Farm.cursor()
        SheDcursor.execute("select * from Farm.Shed ORDER BY date DESC LIMIT 1")
        myresult = SheDcursor.fetchone()
        SheDcursor.close
#select * from Shed;
#+---------------------+-----------+--------+-----------+-----------+
#| date                | mode      | period | LastFlood | NextFlood |
#+---------------------+-----------+--------+-----------+-----------+
#| 2019-12-28 09:56:04 | flowering |     90 | 09:56:04  | 09:56:04  |
#+---------------------+-----------+--------+-----------+-----------+
        try:
                date = myresult[0]
                mode = myresult[1]
                period = myresult[2]
                LastFlood = myresult[3]
                NextFlood = myresult[4]
                return date, mode, period, LastFlood, NextFlood
        except TypeError:
                print "no entry yet"
def Light(mode):
        now = datetime.now().strftime("%H:%M:%S")
        if mode == "Vegetative":
                DayStart = "06:00:00"
                DayEnd = "22:00:00"
        elif mode == "Flowering":
                DayStart = "08:00:00"
                DayEnd = "20:00:00"
        if now > DayStart  and  now < DayEnd:
                GPIO.output(26, GPIO.HIGH)
                GPIO.output(21, GPIO.HIGH)
        else:
                GPIO.output(21, GPIO.LOW)
        Lstatus = GPIO.input(21)
        if Lstatus:
                LStatus = "On"
        else:
                LStatus = "Off"

        return now, LStatus, DayStart, DayEnd

def Flood():
        now = datetime.now().strftime("%H:%M:%S")
        try:
                Shed=dbShedRead()
                date = Shed[0]
                mode = Shed[1]
                period = Shed[2]
                LastFlood = Shed[3]
                NextFlood = Shed[4]
                NextFlood = str(NextFlood)
                PStatus = GPIO.input(12)
                if now > NextFlood:
                        GPIO.output(26, GPIO.HIGH)
                        GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
                        PStatus = GPIO.input(12)
                return PStatus
        except TypeError:
                GPIO.output(26, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
                PStatus = GPIO.input(12)
                return PStatus

def sensorCallback(channel):
        from datetime import datetime as dt
        import datetime
        # Called if sensor output changes
        global vol
        global stat
        now = dt.now()
        nowDate = now.strftime("%Y-%m-%d %H:%M:%S")
        nowTime = now.strftime("%H:%M:%S")
        if GPIO.input(channel):
                try:
                        vol = vol+1

                except:
                        vol = 0
                pass
        else:
                try:
                        vol = vol+1
                except:
                        vol = 0
                pass
        if vol > 0:
                GPIO.output(12, GPIO.LOW)
                try:
                        Shed=dbShedRead()
                        mode = Shed[1]
                        period = Shed[2]
#                       LastFlood = Shed[3]
#                       NextFlood = Shed[4]
                except TypeError:
                        print "no previous entry"
                        period = 90
                        mode = 'Vegetative'
                        LastFlood= nowTime
                LastFlood= nowTime
                NextFlood = datetime.datetime.now() + datetime.timedelta(minutes = int(period))
                NextFlood = NextFlood.strftime("%H:%M:%S")
                Farm = mysql.connector.connect(
                        host="localhost",
                        user="pi",
                        passwd="a-51d41e",
                        database="Farm"
                )
                SheD = Farm.cursor()
#+---------------------+-----------+--------+-----------+-----------+
#| date                | mode      | period | LastFlood | NextFlood |
#+---------------------+-----------+--------+-----------+-----------+
#| 2019-12-28 09:56:04 | flowering |     90 | 09:56:04  | 09:56:04  |
#+---------------------+-----------+--------+-----------+-----------+
                sql = "insert INTO Farm.Shed (date,mode,period,LastFlood,NextFlood) VALUES (%s, %s, %s, %s, %s)"
                val = (nowDate,mode,period,LastFlood,NextFlood)
                SheD.execute(sql, val)
                Farm.commit()
                time.sleep(90)


if __name__ == "__main__":
	global h2owcursor
	thread = BackChemSensors(ReadSensors)
	thread.start()
	initreturn = init()
	time.sleep(1)
	while True:
		os.system('clear')

		try:
			H2O=dbH2ORead()
			date = H2O[0]
			pH = H2O[1]
			EC = H2O[2]
			TDS = H2O[3]
			S = H2O[4]
			SG = H2O[5]
		except TypeError:
			print "no entry yet"
			date = datetime.now()
                try:
                        Shed=dbShedRead()
                        mode = Shed[1]
                        period = Shed[2]
                        LastFlood = Shed[3]
                        NextFlood = Shed[4]
                except TypeError:
                        print "no entry yet"
                        mode = "Vegetative"
	        Light(mode)
                Flood()
                Pstatus = GPIO.input(12)
                if Pstatus:
                        PStatus = "On"
                else:
                        PStatus = "Off"
                Lstatus = GPIO.input(21)
                if Lstatus:
                        LStatus = "On"
                else:
                        LStatus = "Off"
		try:
	#		print datetime.now().strftime("%H:%M:%S") 
        	        print "Lamp Status: ", LStatus
			print "Pump Status: ", PStatus, "NextFlood:", NextFlood
                	print "H2O:", "pH:", "pH", pH, "EC", EC, "TDS", TDS, "S", S, "SG", SG
		except NameError:
			NextFlood = "No entry yet"

		time.sleep(2)

