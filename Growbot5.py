#!/usr/bin/python

# Import required libraries
import os
import sys
import io
import fcntl
import time
import datetime
import RPi.GPIO as GPIO
import mysql.connector
import threading
############################################################################

def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  # Get initial reading
#  HallSensor(22)
  try:
    # Loop until users quits with CTRL-C
    thread = ChemSensors(ReadSensors)
    while True :
	if thread.is_alive() is False:
		thread = ChemSensors(ReadSensors)
		thread.start()
	try:    
                GPIO.add_event_detect(22, GPIO.BOTH, callback=HallSensor, bouncetime=100)
        except:
                pass
#	os.system('clear')
	Light()
	Flood()
	time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

################################################################

def HallSensor(channel):
	# Called if sensor output changes
    	timestamp = time.time()
    	stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    	Farm = mysql.connector.connect(
		host="localhost",
		user="pi",
		passwd="a-51d41e",
		database="Farm"
    	)
    	if GPIO.input(channel) or not GPIO.input(channel):
#		print "Draining"
		time.sleep(1)
    		#GPIO.output(21, GPIO.LOW)
    		Data = Farm.cursor()
    		sql = "UPDATE farmdata SET Hall = '1' WHERE date = (select date from farmdata order by date desc limit 1);"
    		Data.execute(sql)
    		Data.close
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
                #       print(device.query(verb))
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
	while True:
		try:    
                	GPIO.add_event_detect(22, GPIO.BOTH, callback=HallSensor, bouncetime=100)
        	except:
                	pass
		now = datetime.datetime.now()
		now = now.strftime("%Y-%m-%d %H:%M:%S")
		pH = 0
		while pH == 0:
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
		Sum=0
		H2O=dbRead('H2O')
                Floodvol = H2O[7]
	       	Farm = mysql.connector.connect(
                	host="localhost",
                	user="pi",
                	passwd="a-51d41e",
                	database="Farm"
       	 	)
        	h2ocursor = Farm.cursor()
#        	h2ocursor.execute("select hall from Farm.farmdata ORDER BY date DESC LIMIT 20")
		h2ocursor.execute("select sum(Hall) FROM (select date, Hall from farmdata ORDER BY date desc limit 10) t;")
		Hall = h2ocursor.fetchone()
#        	myresult = h2ocursor.fetchall()
#      		for x in myresult:
#			x = int(''.join(map(str, x))) 
#			try:
#				Sum = Sum + x
#			except NameError:
#				Sum = x
		H2O=dbRead('H2O')
                Floodvol = H2O[7]
		Hall = float(''.join(map(str, Hall)))
		print "Hall status: ", Hall
		DataWrite()
		if Hall > 3:
		#if Sum > 9:
                        GPIO.output(21, GPIO.LOW)
			Data = Farm.cursor()
    			sql = "UPDATE farmdata SET Hall = '1' WHERE date = (select date from farmdata order by date desc limit 1);"
    			Data.execute(sql)
    			Data.close
    			Farm.commit()
                        if Floodvol > 1:
                                Floodvol = Floodvol - 1
                        else:
                                Floodvol = '0'
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
                	H2O = Farm.cursor()
                	sql = "INSERT INTO Farm.H2O (date,Temp,pH,EC,TDS,S,SG,FloodVol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        	        val = (now,temp,pH,Ec,TDS,S,SG,Floodvol)
	                H2O.execute(sql, val)
        	        H2O.close 
	                Farm.commit()
			if SinceLastMin > 30:
                                SheD = Farm.cursor()
                                sql = "INSERT INTO Farm.Shed (date,mode,period,LastFlood,NextFlood) VALUES (%s, %s, %s, %s, %s)"
                                val = (now,mode,period,now,NextFlood)
                                SheD.execute(sql, val)
                                SheD.close
                                Farm.commit()
                        print now, "Draining", Floodvol
		elif GPIO.input(21) and not GPIO.input(6):
                        try:
                                Floodvol = Floodvol + 1.5
                        except ValueError:
                                Floodvol = 0
	                now = datetime.datetime.now()
	               	H2O = Farm.cursor()
        	        sql = "INSERT INTO Farm.H2O (date,Temp,pH,EC,TDS,S,SG,FloodVol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
	                val = (now,temp,pH,Ec,TDS,S,SG,Floodvol)
                	H2O.execute(sql, val)
        	        H2O.close 
	                Farm.commit()
                        print now, " Filling", Floodvol
		else:
			try:    
                		GPIO.add_event_detect(22, GPIO.BOTH, callback=HallSensor, bouncetime=100)
        		except:
                		pass
			print now, " Nothin", Floodvol
        		H2O = Farm.cursor()
                        sql = "INSERT INTO Farm.H2O (date,Temp,pH,EC,TDS,S,SG,FloodVol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (now,temp,pH,Ec,TDS,S,SG,Floodvol)
                        H2O.execute(sql, val)
                        H2O.close
			Farm.commit()
			h2ocursor = Farm.cursor()
			h2ocursor.execute("select FloodVol from Farm.H2O ORDER BY date DESC LIMIT 5")
        		myresult = h2ocursor.fetchall()
			for x in myresult:
				x = int(''.join(map(str, x)))
		#		print x	
			if myresult[0] == myresult[1] ==  myresult[2] == myresult[3] == myresult[4]:
					Data = Farm.cursor()
			    		sql = "UPDATE H2O SET FloodVol = '0' WHERE date = (select date from H2O order by date desc limit 1);"
			    		Data.execute(sql)
			    		h2ocursor.close
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
		Vstatus= GPIO.input(6)
		if Vstatus:
			Valve("f")
	        GPIO.output(26, GPIO.HIGH)
               	GPIO.output(21, GPIO.HIGH)   # <---------------- change to HIGH when theres water or a way too check
#		DataWrite()

#############################################################

def Valve(dir):
	now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
	ValveS = GPIO.input(5)
	ValveD = GPIO.input(6)
	if dir == 'f':
		if ValveD:
			GPIO.output(5, GPIO.LOW)
			GPIO.output(6, GPIO.HIGH)
			t_end = time.time() + 13
			while time.time() < t_end:
				Display()
				time.sleep(1)
				DataWrite()
			GPIO.output(5, GPIO.HIGH)
#			DataWrite()
        if dir == 'c':
                if not ValveD:
                        GPIO.output(5, GPIO.LOW)
                        GPIO.output(6, GPIO.LOW)
                        t_end = time.time() + 13
                        while time.time() < t_end:
                                Display()
                                time.sleep(1)
                                DataWrite()
                        GPIO.output(5, GPIO.HIGH)
#			DataWrite()





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
			ValveS = myresult[7]
			Hall = myresult[8]
			return date, main, lights, ExFan, AirPump, WaterPump, ValveS, ValveS, Hall
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





############################3
#
#
#
#############################


# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)
print("Setup GPIO pin as input on GPIO22")

# Set Switch GPIO as input
# Pull high by default
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(12 , GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.BOTH, callback=HallSensor, bouncetime=500)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)                                                        #, initial=GPIO.LOW) # AC WaterPump
GPIO.setup(26, GPIO.OUT)


if __name__=="__main__":
   main()
