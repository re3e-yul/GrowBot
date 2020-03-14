#!/usr/bin/env python
import threading
#from threading import Thread
import RPi.GPIO as GPIO
import time
import datetime
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
	print ""
	print "RE3e presents"
	time.sleep(0.8)
	print "An Evil Scientist SINdicate production"
	time.sleep(0.8)
	print "GrowBot V. (The return of Growbot)"
	time.sleep(1.6)
	print""
	print "Setting up GPIO"
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)							#, initial=GPIO.LOW) # AC Main
        GPIO.setup(21, GPIO.OUT) 							#, initial=GPIO.LOW) # AC Lighs
        GPIO.setup(12, GPIO.OUT) 							#, initial=GPIO.LOW) # AC WaterPump
	print "setting up GPIO Pullbacks"
  	GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)  				#, initiate Hall sensor
  	GPIO.add_event_detect(22, GPIO.BOTH, callback=sensorCallback, bouncetime=900)   #, on Hall call function
        print "Setting up I2C sensors"
	AtlasDetect()
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
def dbRow():
	Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
        global mycursor
	mycursor = Farm.cursor()
        mycursor.execute("select * from Farm.farmdata ORDER BY date DESC LIMIT 1")
        myresult = mycursor.fetchone()
	#+---------------------+--------+-------+---------+-----------+--------+-----------+-------+--------+--------+--------+-------+-----------+-----------+
	#| date                | lights | ExFan | AirPump | WaterPump | period | mode      | pH    | EC     | TDS    | S      | SG    | LastFlood | NextFlood |
	#+---------------------+--------+-------+---------+-----------+--------+-----------+-------+--------+--------+--------+-------+-----------+-----------+
	#| 2019-12-28 09:56:04 | On     | Off   | Off     | Off       |     90 | Flowering | 6.800 | 99.999 | 99.999 | 99.999 | 1.030 | 09:49:16  | 12:49:16  |
	#+---------------------+--------+-------+---------+-----------+--------+-----------+-------+--------+--------+--------+-------+-----------+-----------+
	date = myresult[0]
	lights = myresult[1]
	ExFan = myresult[2]
	AirPump = myresult[3]
	WaterPump = myresult[4]
	period = myresult[5]
	mode = myresult[6]
	pH = myresult[7]
	EC = myresult[8]
	TDS = myresult[9]
	S = myresult[10]
	SG = myresult[11]
	LastFlood = myresult[12]
	NextFlood  = myresult[13]

        return date, lights, ExFan, AirPump, WaterPump, period, mode, pH, EC, TDS, S, SG, LastFlood, NextFlood;

def Light(date,Lights,mode):
	now = strftime("%H:%M:%S")
#	now = "23:00:00"
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

def Flood(date,WaterPump,period,LastFlood, NextFlood):
	now = datetime.datetime.now().strftime("%H:%M:%S")
#	now = "23:55:16"
	NextFlood = str(NextFlood)
	PStatus = GPIO.input(12)
	if now > NextFlood:
		GPIO.output(26, GPIO.HIGH)
                GPIO.output(12, GPIO.LOW)   # <---------------- change to HIGH when theres water or a way too check
		PStatus = GPIO.input(12)
		LastFlood = strftime("%H:%M:%S")
		NextFlood = datetime.datetime.now() + datetime.timedelta(minutes = int(period))
		NextFlood = NextFlood.strftime("%H:%M:%S")
		
	Pstatus = GPIO.input(12)
        if Pstatus:
                PStatus = "On"
        else:
                PStatus = "Off"

	Farm = mysql.connector.connect(
        	host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
                )
        global mycursor
        sql = "INSERT INTO Shed (date,mode,period,LastFlood,NextFlood) VALUES (%s, %s)"
        val = (now,mode,period,LastFlood,NextFlood)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
	PStatus = GPIO.input(12)
	return now, PStatus, period, LastFlood, NextFlood

def Display(mainreturn):
	now = mainreturn[0]
        mode = mainreturn[1]
        DayStart = mainreturn[2]
        DayEnd = mainreturn[3]
        LStatus = mainreturn[4]
        PStatus = mainreturn[5]
        LastFlood = mainreturn[6]
        NextFlood = mainreturn[7]
	period = mainreturn[8]
	print ""
        print "RE3e presents"
        print "An Evil Scientist SINdicate production"
        print "GrowBot V. (The return of Growbot)"
        print ""
        print now, ",System init:", initreturn
        print ""
        print "mode:", mode
        print "Day Start:", DayStart, ", Day End:", DayEnd  
        print "Light Status: ",LStatus 
        print ""
        print "Pump Status: ",PStatus, "Period:", period
        print "Last Flood: ",LastFlood, ", Next Flood: ",NextFlood
	try:
		#EC,TDS,S,SG
		Ec = EC[0]
		TDS = EC[1]
		S = EC[2]
		SG = EC[3]
		print "pH:",pH, "EC:",Ec, "TDS:",TDS,"Salinity:",S,"Specfc Grav:",SG
	except NameError:
                print "pH:",pH

class BackgroundSensors(threading.Thread):

    def __init__(self, function_that_downloads):
        threading.Thread.__init__(self)
        self.runnable = ReadSensors
        self.daemon = True

    def run(self):
        self.runnable()

def ReadSensors():
		global EC
		global pH
		now = strftime("%H:%M:%S")
		pH = Atlas(99,"i")
		while True:
			pH = Atlas(99,"r")
			EC = Atlas(100, 'R')
			Ec = EC[0]
                	TDS = EC[1]
                	S = EC[2]
                	SG = EC[3]

			Farm = mysql.connector.connect(
                		host="localhost",
                		user="pi",
                		passwd="a-51d41e",
                		database="Farm"
        		)
        		global mycursor
			sql = "INSERT INTO H2O (date,pH,EC,TDS,S,SG) VALUES (%s, %s)"
			val = (now,pH,Ec,TDS,S,SG)
			mycursor.execute(sql, val)
			mydb.commit()
			print(mycursor.rowcount, "record inserted.")
			print now,pH,Ec,TDS,S,SG
			time.sleep(5)			
		return pH, EC











def main(initreturn):
	try:
		dbrow = dbRow()
		date = dbrow[0]
		Lights = dbrow[1]
		ExFan = dbrow[2]
		AirPump = dbrow[3]
		WaterPump = dbrow[4]
		period = dbrow[5]
		mode = dbrow[6]
		pH = dbrow[7]
		EC = dbrow[8]
		TDS = dbrow[9]
		S = dbrow[10]
		SG = dbrow[11]
		LastFlood = dbrow[12]
		NextFlood = dbrow[13]

		LightSched = Light(date, Lights, mode)
		now = LightSched[0]
		LStatus = LightSched[1]
		DayStart = LightSched[2]
		DayEnd = LightSched[3]
		#    feed

		FloodSched = Flood(date, WaterPump, period, LastFlood, NextFlood)
		now = FloodSched[0]
		PStatus = FloodSched[1]
		period = FloodSched[2]
		LastFlood = FloodSched[3]
		NextFlood = FloodSched[4]
	#    vent
	#    monitor
	#    calibrate
	except KeyboardInterrupt:
		# Reset GPIO settings
		gpio.cleanup()
		sys.exit(0)
	finally:
		#		print now, mode, DayStart, DayEnd, LStatus, PStatus,LastFlood, NextFlood, period
		PStatus = GPIO.input(12)
		return now, mode, DayStart, DayEnd, LStatus, PStatus, LastFlood, NextFlood, period


if __name__ == "__main__":

	thread = BackgroundSensors(ReadSensors)
	thread.start()
	initreturn = init()
	time.sleep(1)
	while True:
		os.system('clear')
		mainreturn = main(initreturn)
		Display(mainreturn)
		time.sleep(0.7)
