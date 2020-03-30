#!/usr/bin/env python

import os
import threading
import time
import urllib2


class ImageDownloader(threading.Thread):

    def __init__(self, function_that_downloads):
        threading.Thread.__init__(self)
        self.runnable = ReadSensors
        self.daemon = True

    def run(self):
        self.runnable()

def ReadSensors():
#def downloads():
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







thread = ImageDownloader(ReadSensors)
thread.start()
try:
        pHSens = atlas_i2c()
        pH = round(float(pHSens.query('R')), 4)
	print pH
except ValueError: 
#	print "ValueError"
	pass
except NameError:
#	print "NameError"
	pass


try:
        ECSens = atlas_i2c()
        ECs = ECSens.query('R')
	ECs.split(',')
	Con,TDS,Salt,SG = ECs.split(',')
	Con = float (float(Con) / 1000)
	TDS = float (float(TDS) / 1000)
	Salt = float (float(Salt) / 1)
#	print "Conductivity: ", Con             #0.8-1.3 clones/seedlings, 1.3-1.7 veg 1.2-2.0 flo, flush ~0
#	print "Total Disolved Solids: ", TDS    #500-600 ppm clones/seedlings, 800-900 veg 1000-1100 flo, flush 400-500
#	print "Salinity: ", Salt		#~=0.5
#	print "Specific Gravity: ", SG		
	print Con, TDS, Salt, SG
except ValueError: 
#	print "ValueError"
	pass
except NameError:
#	print "NameError"
	pass
thread.is_alive()
