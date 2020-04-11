#! /usr/bin/python
import os
<<<<<<< HEAD
import sys
=======
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
import threading
import time
import urllib2
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import mysql.connector
import datetime
from datetime import datetime
import RPi.GPIO as GPIO

def init():
	os.system('clear')
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)							#, initial=GPIO.LOW) # AC Main
        GPIO.setup(21, GPIO.OUT) 							#, initial=GPIO.LOW) # AC Lighs
        GPIO.setup(12, GPIO.OUT) 							#, initial=GPIO.LOW) # AC WaterPump
        GPIO.setup(5, GPIO.OUT)                                                        #, initial=GPIO.LOW) # AC Lighs
        GPIO.setup(6, GPIO.OUT)
  	GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)  				#, initiate Hall sensor
  	GPIO.add_event_detect(22, GPIO.BOTH, callback=sensorCallback, bouncetime=900)   #, on Hall call function
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
<<<<<<< HEAD
class ChemSensors(threading.Thread):
=======
class ChenSensors(threading.Thread):
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e

    def __init__(self, Read_Chem_Sensors):
        threading.Thread.__init__(self)
        self.runnable = Read_Chem_Sensors

    def run(self):
        self.runnable()
def ReadSensors():
                global EC
                global pH
                while True:
                        now = datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
                        pH = Atlas(99,"r")


                        ECs = Atlas(100,"r")
                        ECs.split(',')
                        Ec,TDS,S,SG = ECs.split(',')
                        Ec = float (float(Ec) / 1000)
                        TDS = float (float(TDS) / 1000)
                        S = float (float(S) / 1)

                        #EC = Atlas(100, 'r')
                        #Ec = EC[0]
                        #TDS = EC[1]
                        #S = EC[2]
                        #SG = EC[3]

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
                        sql = "INSERT INTO Farm.H2O (date,pH,EC,TDS,S,SG) VALUES (%s, %s, %s, %s, %s, %s)"
                        val = (now,pH,Ec,TDS,S,SG)
                        H2O.execute(sql, val)
                        Farm.commit()
                        #print(H2O.rowcount, "record inserted.")
                        H2O.close
                        time.sleep(5)
                return now,pH,Ec,TDS,S,SG
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
#                	LastFlood = Shed[3]
#                	NextFlood = Shed[4]
		except TypeError:
			print "no previous entry"
			period = 10
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
		time.sleep(90)    ## <----------------FIX FOR DRAINTIME

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


def Display():
<<<<<<< HEAD
#        	from datetime import datetime as dt
#        	now = dt.now()
		now = datetime.now()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
=======
        	from datetime import datetime as dt
        	now = dt.now()
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
		try:
			H2O=dbH2ORead()
			date = H2O[0]
			pH = H2O[1]
			EC = H2O[2]
			TDS = H2O[3]
			S = H2O[4]
			SG = H2O[5]
		except TypeError:
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
			ValveS = Act[7]
		except TypeError:
                        print "no entry yet"

<<<<<<< HEAD
        	#Pstatus = GPIO.input(12)
=======
        	Pstatus = GPIO.input(12)
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
        	if Pstatus:
                	PStatus = "On"
        	else:
                	PStatus = "Off"
<<<<<<< HEAD
		#Lstatus = GPIO.input(21)
=======
		Lstatus = GPIO.input(21)
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
        	if Lstatus:
                	LStatus = "On"
        	else:
                	LStatus = "Off"
		print now
		print ""
		print "Lamp Status: ", LStatus
		print "Pump Status: ", PStatus, "\tLastFlood:", LastFlood, "\tNextFlood:", NextFlood
		print "Valve Direc: ",ValveS
		print "Air Pump   : ", AirPump
		print "Exhaust Fan: ", ExFan

		print ""
		print "Chem analysis\t\tpH:", pH, "\tEC:\t", EC
		print "\t\t\t\t\tTDS:\t", TDS
		print "\t\t\t\t\tS:\t", S
		print "\t\t\t\t\tSG:\t", SG
		return mode

def Light(mode):
<<<<<<< HEAD
#        from datetime import datetime as dt
#        now = str(dt.now())
	now = datetime.now()
        now = now.strftime("%H:%M:%S")

        Act = dbDataRead()
        date = Act[0]
        main = Act[1]
#        LStatus = Act[2]
        ExFan = Act[3]
        AirPump = Act[4]
        PStatus = Act[5]
        ValveS = GPIO.input(5)
        ValveD = GPIO.input(6)


        if mode == "Vegetative":
		print (mode)
		DayStart = "06:00:00"
       	        DayEnd = "22:17:00"
        elif mode == "Flowering":
               	DayStart = "08:00:00"
               	DayEnd = "20:00:00"
		print (DayStart, DayEnd)
	if now > DayStart  and  now < DayEnd:
		Lstatus = GPIO.input(21)
		if Lstatus == '0':
	               	GPIO.output(26, GPIO.HIGH)
	               	GPIO.output(21, GPIO.HIGH)
			print ("Light on",now ,DayStart, DayEnd)
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
                	val = (now, main, LStatus, ExFan, AirPump, PStatus, ValveS, ValveD)
                	time.sleep(1)
                	SheD.execute(sql, val)
                	Farm.commit()

		
	else:
		Lstatus = GPIO.input(21)
                if Lstatus == '1':
	               	GPIO.output(21, GPIO.LOW)
			print ("Light off")
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
                        val = (now, main, LStatus, ExFan, AirPump, PStatus, ValveS, ValveD)
                        time.sleep(1)
                        SheD.execute(sql, val)
                        Farm.commit()
	
=======
        from datetime import datetime as dt
        now = str(dt.now())
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
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
        if Lstatus:
                LStatus = "On"
        else:
                LStatus = "Off"
<<<<<<< HEAD
	print (LStatus)
	time.sleep(5)
=======
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
        return now, LStatus, DayStart, DayEnd
def Flood():
        from datetime import datetime as dt
        now = dt.now()
	Valve("f")
	try:
		Shed=dbShedRead()
        	date = Shed[0]
        	mode = Shed[1]
        	period = Shed[2]
                LastFlood = Shed[3]
                NextFlood = Shed[4]
	        NextFlood = str(NextFlood)
	        PStatus = GPIO.input(12)
#		print  "NextFlood:", now,"NextFlood:", NextFlood
	        if now > NextFlood:
		        GPIO.output(26, GPIO.HIGH)
                	GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
                	PStatus = GPIO.input(12)
<<<<<<< HEAD

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
                val = (now, main, LStatus, ExFan, AirPump, PStatus, ValveS, ValveD)
                time.sleep(1)
                SheD.execute(sql, val)
                Farm.commit()


=======
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
		return PStatus
	except TypeError:
		GPIO.output(26, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
                PStatus = GPIO.input(12)
		return PStatus
def Valve(dir):
<<<<<<< HEAD
#        from datetime import datetime as dt
#        now = dt.now()
	now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
=======
        from datetime import datetime as dt
        now = dt.now()
>>>>>>> 967a207605df579e23b5c11d08c66f6cdfc6de1e
	Act = dbDataRead()
	date = Act[0]
	main = Act[1]
	LStatus = Act[2]
	ExFan = Act[3]
	AirPump = Act[4]
	PStatus = Act[5]
	ValveS = GPIO.input(5)
	ValveD = GPIO.input(6)

	if dir == "c":
		if not ValveD:
			GPIO.output(5, GPIO.HIGH)
			GPIO.output(6, GPIO.HIGH)
			time.sleep(13)
	if dir == "f":
		if ValveD:
			GPIO.output(5, GPIO.HIGH)
			GPIO.output(6, GPIO.HIGH)
			time.sleep(13)

	ValveS = GPIO.input(5)
	ValveD = GPIO.input(6)

	if ValveS:
		ValveS = "On"
	else:
		ValveS = "Off"
	if ValveD:
		ValveD = "Cycle"
	else:
		ValveD = "Flood"

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
		val = (now, main, LStatus, ExFan, AirPump, PStatus, ValveS, ValveD)
		time.sleep(1)
		SheD.execute(sql, val)
		Farm.commit()



if __name__ == "__main__":

	thread = ChemSensors(ReadSensors)
	thread.start()
	initreturn = init()

    
        time.sleep(1)
        while True:
		try:
			os.system('clear')
			mode = Display()
			Flood()
			Light(mode)
		except KeyboardInterrupt:
			# Reset GPIO settings
			gpio.cleanup()
			sys.exit(0)
