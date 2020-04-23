#! /usr/bin/python
import os
import sys
import threading
import time
import urllib2
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import mysql.connector
import datetime
#from datetime import datetime
import RPi.GPIO as GPIO

def init():
	os.system('clear')
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)							#, initial=GPIO.LOW) # AC Main
        GPIO.setup(21, GPIO.OUT) 							#, initial=GPIO.LOW) # AC Lighs
        GPIO.setup(12, GPIO.OUT) 							#, initial=GPIO.LOW) # AC WaterPump
        GPIO.setup(5, GPIO.OUT)                                                         #, initial=GPIO.LOW) # on/off 3w
	GPIO.setup(20, GPIO.OUT)                                                        #, initial=GPIO.LOW) #air pump
        GPIO.setup(16, GPIO.OUT)                                                         #, initial=GPIO.LOW) #ExFan
        GPIO.setup(6, GPIO.OUT)								#, initial=GPIO.LOW) # Dir 3w
  	GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)  				#, initiate Hall sensor
  	GPIO.add_event_detect(22, GPIO.BOTH, callback=sensorCallback, bouncetime=900)   #, on Hall call function
	GPIO.output(5, GPIO.HIGH)
#	AtlasDetect()
	return "ok"


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
        	self.file_write.clos
def Atlas(addr,verb):
        try:
                device = atlas_i2c()  # creates the I2C port object, specify the address or bus if necessary
                device.set_i2c_address(int(addr))
                try:
                        Type = device.query('i')[3:5]
                        value = (device.query(verb))
                #       print(device.query(verb))
                except IOError:
                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
        except IOError:
                "No I2C port detected"
        return value
class ChemSensors(threading.Thread):

    def __init__(self, Read_Chem_Sensors):
        threading.Thread.__init__(self)
        self.runnable = Read_Chem_Sensors

    def run(self):
        self.runnable()
def ReadSensors():
                global EC
                global pH
                while True:
                        now = datetime.datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
                        try:
				pH = Atlas(99,"r")
			except ValueError:
#				pH = Atlas(99,"r")
				pass

			try:
	                        ECs = Atlas(100,"r")
	                        ECs.split(',')
	                        Ec,TDS,S,SG = ECs.split(',')
	                        Ec = float (float(Ec) /1.0)
	                        TDS = float (float(TDS) / 1.0)
	                        S = float (float(S) * 1000)
				SG = float (float(SG) / 1.0)
			except ValueError:
			    	ECs = Atlas(100,"r")
                                ECs.split(',')
                                Ec,TDS,S,SG = ECs.split(',')
                                Ec = float (float(Ec) /1.0)
                                TDS = float (float(TDS) / 1.0)
                                S = float (float(S) * 1000)
                                SG = float (float(SG) / 1.0)
				pass
			path = "/sys/bus/w1/devices/"
			dir_list = os.listdir(path)
			for path in dir_list:
	        		if '28' in path:
        	        		path = "/sys/bus/w1/devices/" + path + "/w1_slave"
			f = open(path, "r")
			for last_line in f:
        			pass
			temp = last_line.split()
			temp = str(temp[-1])
			temp = (float(temp.strip("t=")) /1000 )

			#print temp,'c'
			if temp > 28:
				GPIO.output(16, GPIO.HIGH)
			elif temp < 27:
				GPIO.output(16, GPIO.LOW)
                        Farm = mysql.connector.connect(
                                host="localhost",
                                user="pi",
                                passwd="a-51d41e",
                                database="Farm"
                        )
#                       +---------------------+-------+------+------+------+------+
#                       | date                | pH    | EC   | TDS  | S    | SG   |
#                       +---------------------+-------+------+------+------+------+
#                       | 2019-12-20 09:56:04 | 6.800 |  100 |  100 |  100 |    1 |
#                       +---------------------+-------+------+------+------+------+

                        H2O = Farm.cursor()
                        sql = "INSERT INTO Farm.H2O (date,Temp,pH,EC,TDS,S,SG) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        val = (now,temp,pH,Ec,TDS,S,SG)
			try:
	                        H2O.execute(sql, val)
	                        Farm.commit()
			except UnboundLocalError:
				pass
                        H2O.close
		print (now,Temp,pH,Ec,TDS,S,SG)
		time.sleep(5)
                return now,Temp,pH,Ec,TDS,S,SG


def sensorCallback(channel):
#	from datetime import datetime as dt
 	import datetime
	# Called if sensor output changes
  	global vol
  	global stat
	now = datetime.datetime.now()
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
	print ("vol", vol)
	time.sleep(3)
	if vol > 0:
		GPIO.output(12, GPIO.LOW)
	else:
                try:
			Shed=dbShedRead()
                	mode = Shed[1]
                	period = Shed[2]
		except TypeError:
			print "no previous entry"
			period = 10
			mode = 'Vegetative'
		LastFlood= nowDate
		NextFlood = datetime.datetime.now() + datetime.timedelta(hours = int(period))
                NextFlood = NextFlood.strftime("%Y-%m-%d %H:%M:%S")
		print ("LastFlood", LastFlood, "NextFlood", NextFlood)
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
        	sql = 'update Farm.Shed set mode = %s ,period = %s, LastFlood = %s ,NextFlood = %s where date = ( select max(date))'
		val = (mode,period,LastFlood,NextFlood)
                SheD.execute(sql, val)
                Farm.commit()

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
		Temp = myresult[1]
		pH = myresult[2]
		EC = myresult[3]
		TDS = myresult[4]
		S = myresult[5]
		SG = myresult[6]
		return date, Temp, pH, EC, TDS, S, SG
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
def dbDataRead():
        Farm = mysql.connector.connect(
                host="localhost",
                user="pi",
                passwd="a-51d41e",
                database="Farm"
        )
        #global mycursor
        SheDcursor = Farm.cursor()
        SheDcursor.execute("select * from Farm.farmdata ORDER BY date DESC LIMIT 1")
        myresult = SheDcursor.fetchone()
        SheDcursor.close
#select * from farmdata order by date desc limit 1;
#+---------------------+------+--------+-------+---------+-----------+------+------+
#| date                | main | lights | ExFan | AirPump | WaterPump | 3wv  | 3wvD |
#+---------------------+------+--------+-------+---------+-----------+------+------+
#| 2020-03-21 15:39:09 | On   | On     | Off   | Off     | Off       | On   | Circ |
#+---------------------+------+--------+-------+---------+-----------+------+------+
	try:
		date = myresult[0]
		main = myresult[1]
		lights = myresult[2]
		ExFan = myresult[3]
		AirPump = myresult[4]
		WaterPump = myresult[5]
		ValveS = myresult[6]
		ValveS = myresult[7]
		return date, main, lights, ExFan, AirPump, WaterPump, ValveS, ValveS
        except TypeError:
                print "no entry yet"

def DataWrite():
        Date = datetime.datetime.now()
        Date = Date.strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        now = now.strftime("%H:%M:%S")

        main = GPIO.input(26)
        Lights = GPIO.input(21)
	APump = GPIO.input(20)
        ExFan = GPIO.input(16)
        WPump = GPIO.input(12)
        ValveS = GPIO.input(5)
        ValveD = GPIO.input(6)
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
        Farm.commit()


def Display():
		now = datetime.datetime.now()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
		try:
			H2O=dbH2ORead()
			date = H2O[0]
			Temp = H2O[1]
			pH = H2O[2]
			EC = H2O[3]
			TDS = H2O[4]
			S = H2O[5]
			SG = H2O[6]
		except TypeError:
			Temp ='0'
			pH ='0'
			EC ='0'
			TDS ='0'
			S ='0'
			SG ='0'
			print "no entry yet"
		try:
			Shed=dbShedRead()
			date = Shed[0]
	                mode = Shed[1]
        	        period = Shed[2]
        	        LastFlood = Shed[3]
        	        NextFlood = Shed[4]
                except TypeError:
                        print "no entry yet"
			mode = "Vegetative"
		try:
			Act=dbDataRead()
			date = Act[0]
			main = Act[1]
			LStatus = Act[2]
			ExFan = Act[3]
			AirPump = Act[4]
			PStatus = Act[5]
			ValveS = Act[6]
			ValveD = Act[7]
		except TypeError:
                        print "no entry yet"
			date = now
			main = GPIO.input(26)
			LStatus = GPIO.input(26)
			ExFan = GPIO.input(16)
			AirPump = GPIO.input(20)
			PStatus = GPIO.input(12)
			ValveS = GPIO.input(5)
			ValveD = GPIO.input(6)
		main = GPIO.input(26)
                if main:
                        main = "On"
                else:
                        main = "Off"

		ValveS = GPIO.input(5)
		if ValveS:
                        ValveS = "Off"
                else:
                        ValveS = "On"

		ValveD = GPIO.input(6)
                if ValveD:
                        ValveD = "Cycle"
                else:
                        ValveD = "Flood"

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

		AirPump = GPIO.input(20)
                if AirPump:
                        AirPump = "On"
                else:
                        AirPump = "Off"

                ExFan = GPIO.input(16)
		if ExFan:
                        ExFan = "On"
                else:
                        ExFan = "Off"
		os.system('clear')
		print now
		print ""
		print "status     : ", main
		print "Lamp Status: ", LStatus, "      Mode:     ",mode
		print "Pump Status: ", PStatus, "     LastFlood:", LastFlood, "     NextFlood:", NextFlood
		print "Valve      : ",ValveS, "     Dir:", ValveD
		print "Air Pump   : ", AirPump
		print "Exhaust Fan: ", ExFan

		print ""
		print "Chem analysis     t=",Temp,"c     pH:", pH, "        EC:     ", EC
		print "                                                 TDS:     ", TDS
		print "                                                   S:     ", S
		print "                                                  SG:     ", SG
		return mode

def Light(mode):
        Date = datetime.datetime.now()
        Date = Date.strftime("%Y-%m-%d %H:%M:%S")
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
               	GPIO.output(21, GPIO.HIGH)
        else:
               	GPIO.output(21, GPIO.LOW)
		#print ("Light off")
	LStatus = GPIO.input(21)

def Flood():
	Date = datetime.datetime.now()
        Date = Date.strftime("%Y-%m-%d %H:%M:%S")
	try:
		Shed=dbShedRead()
                mode = Shed[1]
		period = Shed[2]
                NextFlood = Shed[4]
		PStatus = GPIO.input(12)
		NextFlood = str(NextFlood)

		if Date > NextFlood  and PStatus == 0:
			Valve("f")
		        GPIO.output(26, GPIO.HIGH)
                	GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check

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
                	val = (Date,mode,period,Date,NextFlood)
                	SheD.execute(sql, val)
                	Farm.commit()
			time.sleep(2)

	except TypeError:
		GPIO.output(26, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
                PStatus = GPIO.input(12)
		return PStatus
def Valve(dir):
	now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
	ValveS = GPIO.input(5)
	ValveD = GPIO.input(6)
	if dir == 'c':
		if not ValveD:
			print dir
			GPIO.output(5, GPIO.LOW)
			GPIO.output(6, GPIO.HIGH)
			t_end = time.time() + 13
			while time.time() < t_end:
				os.system('clear')
				Display()
				time.sleep(1)
				DataWrite()
			GPIO.output(5, GPIO.HIGH)

        if dir == 'f':
                if not ValveD:
                        print dir
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.LOW)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                os.system('clear')
                                Display()
                                time.sleep(1)
                                DataWrite()
                        GPIO.output(5, GPIO.HIGH)

if __name__ == "__main__":
	thread = ChemSensors(ReadSensors)
	initreturn = init()
        while True:
		if thread.is_alive() is False:
			thread = ChemSensors(ReadSensors)
			thread.start()
		try:
#			os.system('clear')
			mode = Display()
			Light(mode)
			Flood()
			time.sleep(1)
			DataWrite()

                except KeyboardInterrupt:
                        # Reset GPIO settings
                        GPIO.cleanup()
                        os._exit(1)
