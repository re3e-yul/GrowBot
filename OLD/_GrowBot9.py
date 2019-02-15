#!/usr/bin/python
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import sys
import time
import datetime
import threading
import MySQLdb
import RPi.GPIO as GPIO
import plotly.plotly as py
from plotly.graph_objs import Scatter, Bar, Layout, Figure, Data, Stream, YAxis

def readDB():
	global date
	global Lights
	global AirPump
	global WaterPump
	global period
	global HighLevel
	global MidLevel
	global LowLevel
	global Level
	global mode
	global pH
	global LampTemp
	global SoilTemp
	global LastFlood
	global NextFlood
        conn = MySQLdb.connect(host="localhost", user="pi", passwd="a-51d41e", db="Farm")
        cursor = conn.cursor()
        cursor.execute('select date, Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood from farmdata order by date desc limit 1');
        data = cursor.fetchall()
        for row in data :
                date = row[0]
		Lights = row[1]
		AirPump = row[2]
		WaterPump = row[3]
		period = row[4]
		HighLevel = row[5]
		MidLevel = row[6]
		LowLevel = row[7]
		Level = row[8]
		mode = row[9]
		pH = row[10]
		LampTemp = row[11]
		SoilTemp = row[12]
		LastFlood = row[13]
		NextFlood = row[14]         
        cursor.close ()
        conn.close ()
 	return date, Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood

def WriteDB(Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood):
	date = datetime.datetime.now()
	conn = MySQLdb.connect(host="localhost", user="pi", passwd="a-51d41e", db="Farm")
        cursor = conn.cursor()
	try:
        	cursor.execute("INSERT INTO farmdata VALUES (date, Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood)", (date, Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood))
		conn.commit()
	except:
   		conn.rollback()
	cursor.close ()
	conn.close()

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
try:
        pHSens = atlas_i2c()
        pH = round(float(pHSens.query('R')), 3)
except ValueError: 
	pass
except NameError:
	pass

def setupPlotly():
	global stream
	global stream1
	global stream2
	global stream3
        username = 'eric.soulliage'
        api_key = 'bdTewCudMX1yX1pkwnby'
        stream_token = 'itbrfoxov0'       #temp0
        stream_token1 = '8fhj7e1lcz'      #temp1
        stream_token2 = 'wn1s29to9p'      #pH
        stream_token3 = 's2dgh9mik3'      #Level
        #stream_token4 = 'o68awkd2c9'
        #stream_token5 = 'j1o6oz2goz'
        #stream_token6 = '6eho02sw40'
        try:
                py.sign_in(username, api_key)
        except:
                print "Error cant login to plottly"
        pass
        Temp0 = Scatter(
                x=[],
                y=[0, 100],
                name='Temp Lamp',
                mode='lines',
                line=dict(
                        width=2,
                        color='rgb(0, 0, 0)'
                        ),
                stream=dict(
                        token=stream_token,
                        #maxpoints=1500
                        )
                )

        Temp1 = Scatter(
                x=[],
                y=[0, 100],
                mode='lines',
                name='Temp medium',
                line=dict(
                        width=2,
                        color='rgb(0, 0, 255)'
                ),
                stream=dict(
                        token=stream_token1,
                        #maxpoints=1500
                        )
                )

        pH = Scatter(
                x=[],
                y=[0, 10],
                mode='lines',
                name='pH',
                yaxis='y2',
                line=dict(
                        width=2,
                        color='rgb(96, 0, 164)'
                ),
                stream=dict(
                        token=stream_token2,
                        #maxpoints=1500
                )
        )

	BedLevel = Scatter(
                x=[],
                y=[0, 100],
                mode='lines',
                name='BedLevel',
		fill='tozeroy',
                line=dict(
                        width=2,
                        color='rgb(0, 0, 255)',
			shape="spline",
			smoothing=0.3
                ),
                stream=dict(
                        token=stream_token3,
                        #maxpoints=1500
                        )
                )


	layout = Layout(
        	title='GrowBot3',
        	yaxis=dict(
            		title='Temps & % ',
            		range=[0, 100],
            		autorange=False,
            		zeroline=True,
        		),
        	yaxis2=dict(
            		title='pH',
			side='right',
            		range=[0, 10],
            		autorange=False,
            		zeroline=True,
           		titlefont=dict(
                	color='rgb(148, 103, 189)'
            		),
            	tickfont=dict(
                	color='rgb(148, 103, 189)'
           		),
            	overlaying='y',
        	)
    	)


	fig = Figure(data=[Temp0, Temp1, pH, BedLevel], layout=layout)
        try:
                print py.plot(fig, filename='GrowBot6')
        except:
                print "error print to plottly"
        pass
    ###################################
    #                                 #
    # open ploty streams for writting #
    #                                 #
    ###################################

        stream = py.Stream(stream_token)
        stream.open()
        stream1 = py.Stream(stream_token1)
        stream1.open()
        stream2 = py.Stream(stream_token2)
        stream2.open()
        stream3 = py.Stream(stream_token3)
        stream3.open()

def printit(Temp0, Temp1,  pH, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, Level):
	
        now = datetime.datetime.now()
        now = now.strftime('%H:%M:%S')
        #################
        #               #
        # Cli interface #
        #               #
        #################
	
        os.system('clear')
        print now
        print "Evil Science Society"
        print "GrowBot 3"
        print ""
        print "Cycle :", Cycle, "(TimeOn:",TimeOnSTR, "TimeOff:",TimeOffSTR,")"
        print "Soil moisture trigger :", MoistTrig, "%"
        try:
                print "Last flood: ",FloodTime
                print "Next flood: ",NextFloodTime
        except NameError:
                print ""
        pass
        print " "
        print "Lamp Temp  ", Temp0,"C"
        print "Medium Temp ", Temp1, "C"
        print "Moist(0)   ", Moist1, "%"
        print "Moist(1)   ", Moist0, "%"
        print "pH         ", pH
        print " "
        print "Light Status    :", LightStatusTxt
        print "Pump Status     :", PumpStatusTxt
        print "Air Pump Status :", AirStatusTxt
        print " "
        print "High Level    : ", LevelH
        print "Mid Level     : ", LevelM
        print "Low Level     : ", LevelL

def Plotit():
	threading.Timer(15,  Plotit).start()
	readDB()

	###############
        #              #
        # plot graphic #
        #              #
        ################
	try:
	        stream.write({'x': date, 'y': LampTemp,})
	except:
		print "error print LampTemp to plottly"
	pass
	try:
	       	stream1.write({'x': date, 'y': SoilTemp})
        except:
                print "error print RoomTemp to plottly"
        pass
        try:
		stream2.write({'x': date, 'y': pH})
        except:
                print "error print pH to plottly"
        pass
        try:
		stream3.write({'x': date, 'y': Level})
        except:
                print "error print BedLevel to plottly"
        pass


def LightIt(TurnOn, TurnOff):
  	now = datetime.datetime.now()
 	LightPin = 18
	if (now >= TurnOn and now <= TurnOff):	
		GPIO.output(Light, GPIO.LOW)
	else:
        	GPIO.output(Light, GPIO.HIGH)

def AerateIt():
	now = datetime.datetime.now()
	minutes = now.minute
	lastdigit = int(repr(minutes)[-1])
	Air = 14
	if ( lastdigit > 6):
		GPIO.output(Air, GPIO.LOW)
	else:
        	GPIO.output(Air, GPIO.HIGH)

def WaterIt(period, NextFlood):
	now = str(datetime.datetime.now())
	NextFlood = str(NextFlood) 
	if (now > NextFlood):
		GPIO.output(Pump, GPIO.HIGH)
		Level += Level
	
	
def DrainIt(channel):
  	# Called if sensor output changes
  	global vol
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
  	try:
		print  vol 
  	except:
		print "V"  
  	pass
	return vol
def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  try:
    # Loop until users quits with CTRL-C
    #while True :
    t_end = time.time() + 1
    while time.time() < t_end:
      time.sleep(0.1)


def TempSensors():
        fileHandle = open ( '/sys/bus/w1/devices/28-000006911175/w1_slave',"r" )
        lineList1 = fileHandle.readlines()
        fileHandle.close()
        ligne1 = int((lineList1[-1].split()[-1]+'\n')[2:])
        Temp1 = float(ligne1) / 1000

        fileHandle2 = open ( '/sys/bus/w1/devices/28-0000068f125a/w1_slave',"r" )
        lineList2 = fileHandle2.readlines()
        fileHandle.close()
        ligne2 = int((lineList2[-1].split()[-1]+'\n')[2:])
        Temp2 = float(ligne2) / 1000
        return Temp1, Temp2

def ReadSensors():
	threading.Timer(5, ReadSensors).start()
    	global Temp0
    	global Temp1
    	global pH
    	global MoistTrig
    	global LightStatus
    	global LightStatusTxt
    	global PumpStatus
    	global PumpStatusTxt
   	global AirStatus
    	global AirStatusTxt
    	global LevelH
    	global LevelM
    	global LevelL
    	global TankLevel
    	global Light
	Pump = 15
    	Air = 14
    	Light = 18
    	SwitchLow = 5
    	SwitchMid = 6
    	SwitchHigh = 13
	GPIO.setup(SwitchHigh, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(SwitchMid, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(SwitchLow, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) 
  	LightStatus = GPIO.input(Light)
    	PumpStatus = GPIO.input(Pump)
    	AirStatus = GPIO.input(Air)
	SwitchHigh = GPIO.input(SwitchHigh)
	SwitchMed = GPIO.input(SwitchMed)
	SwitchLow = GPIO.input(SwitchLow)
    	LampTemp = TempSensors()[0]
    	SoilTemp = TempSensors()[1]
    	pHSens = atlas_i2c()        # creates the I2C port object for pH sensor
	try:
    		OldpH = pH
    	except:
        	OldpH = "0"
    	try:
    		pH = round(float(pHSens.query('R')), 3)
    	except ValueError:
		pH = OldpH
    	pass
	
	if (GPIO.input(SwitchHigh) == 1 ):
        	LevelH = "on"
    	else:
       	 	LevelH = "off"

    	if (GPIO.input(SwitchMid) == 1):
        	LevelM = "on"
    	else:
        	LevelM = "off"

    	if ( GPIO.input(SwitchLow) == 1):
        	LevelL = "off"
    	else:
       		LevelL = "on"

    	if (LightStatus == 0):
        	LightStatusTxt = "On"
    	else:
		LightStatusTxt = "Off"

    	if (PumpStatus == 0):
        	PumpStatusTxt = "On"
    	else:
        	PumpStatusTxt = "Off"		

	AirStatus = GPIO.input(Air)
    	if (AirStatus == 0):
        	AirStatusTxt = "On"
    	else:
       		AirStatusTxt = "Off"
	return LightStatusTxt, AirStatusTxt, PumpStatusTxt, pH,  HighLevel, MidLevel, LowLevel, LampTemp, SoilTemp

##########################################################################################################

GPIO.setmode(GPIO.BCM)      # set GPIO to board numbering
GPIO.setwarnings(False)
Pump = 15                  #Pump control is on pin 15 of the GPIO Header
Light = 18                 #Light control is on pin 15 of the GPIO Header
Fan = 21                   #Fan  control is on pin 15 of the GPIO Header
Air = 14
BedEnable = 17
BedSelect = 27
SwitchLow = 23
SwitchMid = 24
SwitchHigh = 25
Drain = 22

GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(Light, GPIO.OUT)
GPIO.setup(Air, GPIO.OUT)
GPIO.setup(BedEnable, GPIO.OUT)
GPIO.setup(BedSelect, GPIO.OUT)
GPIO.setup(SwitchHigh, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(SwitchMid, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(SwitchLow, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(Drain, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

LightStatus = GPIO.input(Light)
PumpStatus = GPIO.input(Pump)
AirStatus = GPIO.input(Air)

now = datetime.datetime.now()
if len(sys.argv) > 1:
	for arg in sys.argv:
		
		if arg == "-f" or arg == "-F":
			mode = "Flowering"
			TurnOn = now.replace(hour=8, minute=00, second=0)
		        TurnOff = now.replace(hour=20, minute=00, second=0)
		elif arg == "-F":
			mode = "Flowering"
			TurnOn = now.replace(hour=8, minute=00, second=0)
		        TurnOff = now.replace(hour=20, minute=00, second=0)
		elif arg == "-v" or arg == "-V":
			mode = "Vegetative"
                        TurnOn = now.replace(hour=8, minute=00, second=0)
		        TurnOff = now.replace(hour=20, minute=00, second=0)
		elif arg == "-V":
			mode = "Vegetative"
                        TurnOn = now.replace(hour=8, minute=00, second=0)
		        TurnOff = now.replace(hour=20, minute=00, second=0)
		elif arg == "-FF":
			ForceFlood = "1"
		elif arg.isdigit():
			period = arg
else:
  	print "Usage: GrowBot6.sh -fF/-gG [Hour period] -FF "   	
	sys.exit()

setupPlotly()
Plotit()
GPIO.add_event_detect(22, GPIO.BOTH, callback=DrainIt, bouncetime=200)
while True:

	readDB()	
#	print date, Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood
	ReadSensors()
	printit(LampTemp, SoilTemp, pH, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, Level)
	LightIt(TurnOn, TurnOff)
	WaterIt(period, NextFlood) 
  	AerateIt()
	WriteDB(Lights, AirPump, WaterPump, period, HighLevel, MidLevel, LowLevel, Level, mode, pH, LampTemp, SoilTemp, LastFlood, NextFlood)
	time.sleep(2)

 
