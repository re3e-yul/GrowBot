#!/usr/bin/python

import sys
import spidev
import RPi.GPIO as GPIO # This is the GPIO library we need to use the GPIO pins on the Raspberry Pi
import smtplib # This is the SMTP library we need to send the email notification
import time # This is the time library, we need this so we can use the sleep function
import os
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import datetime
import string # helps parse strings
import commands
import plotly.plotly as py
from plotly.graph_objs import Scatter, Bar, Layout, Figure, Data, Stream, YAxis
import readadc
import threading
import re
global TankLevel

def Plotly_setup():
	#######################
	#                     #
	# PLOTTLY setup       #
	#                     #
	#######################
	global stream
	global stream1
	global stream2
	global stream3
	global stream4
	global stream5
	global stream5
	global stream6
	username = 'eric.soulliage'
    	api_key = 'bdTewCudMX1yX1pkwnby'
    	stream_token = 'itbrfoxov0'
    	stream_token1 = '8fhj7e1lcz'
    	stream_token2 = 'wn1s29to9p'
    	stream_token3 = 's2dgh9mik3'
    	stream_token4 = 'o68awkd2c9'
    	stream_token5 = 'j1o6oz2goz'
    	stream_token6 = '6eho02sw40'
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
            		maxpoints=1500
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
            		maxpoints=1500
        		)
    		)

    	Moist0 = Scatter(
        	x=[],
	        y=[0, 100],
        	mode='lines',
	        name='GrowPod1 Moist%',
        	line=dict(
		        width=2,
            		color='rgb(0, 255, 0)'
        		),
        	stream=dict(
            		token=stream_token2,
            		maxpoints=1500
        		)
    		)

    	Moist1 = Scatter(
        	x=[],
	        y=[0, 100],
        	mode='lines',
	        name='GrowPod2 Moist%',
        	line=dict(
	            width=2,
        	    color='rgb(0, 128, 0)'
        		),
        	stream=dict(
            		token=stream_token3,
            		maxpoints=1500
        		)
   		)

    	Moisttrig = Scatter(
        	x=[],
	        y=[0, 100],
        	mode='lines',
	        name='Moist Trig %',
        	line=dict(
		        width=2,
            		color='rgb(255, 0, 0)'
        		),
        	fill='tozeroy',
	        stream=dict(
            		token=stream_token4,
            		maxpoints=1500
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
            		token=stream_token5,
            		maxpoints=1500
        		)
    		)
    
	Pump = Bar(
        	x=[],
	        y=[0, 100],
        	name='Pump',
	        yaxis='y',
        	marker=dict(
            		color='rgb(0,0,204)'
        		),
        	opacity=0.4,
        	stream=dict(
            		token=stream_token6,
            		maxpoints=1500
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
    	fig = Figure(data=[Temp0, Temp1, Moist0, Moist1, Moisttrig, pH, Pump], layout=layout)
    	try:
        	print py.plot(fig, filename='GrowBot2')
    	except:
        	print "error print to plottly"
    	pass
    ###################################
    #                                 #
    # open ploty streams for writting #
    #                                 #
    ###################################
    	i = 0
	stream = py.Stream(stream_token)
    	stream.open()
    	stream1 = py.Stream(stream_token1)
    	stream1.open()
    	stream2 = py.Stream(stream_token2)
    	stream2.open()
    	stream3 = py.Stream(stream_token3)
    	stream3.open()
    	stream4 = py.Stream(stream_token4)
    	stream4.open()
    	stream5 = py.Stream(stream_token5)
    	stream5.open()
    	stream6 = py.Stream(stream_token6)
    	stream6.open()

class atlas_i2c:
    	long_timeout = 1.5  # the timeout needed to query readings and calibrations
    	short_timeout = .5  # timeout for regular commands
    	default_bus = 1  # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
    	default_address = 99  # the default address for the pH sensor

    	def __init__(self, address=default_address, bus=default_bus):
       		# open two file streams, one for reading and one for writing
        	# the specific I2C channel is selected with bus
        	# it is usually 1, except for older revisions where its 0
        	# wb and rb indicate binary read and write
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
            		char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))  # change MSB to 0 for all received characters except the first and get a list of characters
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


#########################################################################################################################
#                                                                                                                       #
#########################################################################################################################
#                                                                                                                       #
#########################################################################################################################


def DigitH2o(channel):
        #check valid channel
        if ((channel>7)or(channel<0)):
                return -1
        spi = spidev.SpiDev()       # create SPI ports for Analog to Digital Converter
	spi.open(0,0)              # set port for reading
        # Preform SPI transaction and store returned bits in 'r'
        r = spi.xfer([1, (8+channel) << 4, 0])

        #Filter data bits from retruned bits
        adcOut = int(((r[1]&3) << 8) + r[2])
        percent = int(100 - round(adcOut/10.24,3))
        analog =int((3.3 * percent / 100))
        return analog, adcOut, percent

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

def printit(Temp0, Temp1, Moist0, Moist1, pH, MoistTrig, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, TankLevel):
	now = datetime.datetime.now()
	now = now.strftime('%H:%M:%S')
	#################
	#               #
	# Cli interface #
	#               #
	#################

	TimeOnSTR = TurnOn.strftime('%H:%M:%S')
	TimeOffSTR = TurnOff.strftime('%H:%M:%S')
	with open('/var/www/GTTrig.log', 'r') as myfile:
        	MoistTrig = int(re.sub('[^0-9]','', (myfile.read())))
	        myfile.close()
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
	#print "Tank level    : ", TankLevel


def plotit():
  	threading.Timer(3, plotit).start()
	now = datetime.datetime.now()
	now = now.strftime('%H:%M:%S')
	###############
	#              #
	# plot graphic #
	#              #
	################

	stream.write({'x': now, 'y': Temp0})
	stream1.write({'x': now, 'y': Temp1})
	stream2.write({'x': now, 'y': Moist1})
	stream3.write({'x': now, 'y': Moist0})
	stream4.write({'x': now, 'y': MoistTrig})
	stream5.write({'x': now, 'y': pH})
	stream6.write({'x': now, 'y': TankLevel})

def AeroPump():
	now = datetime.datetime.now()
	minutes = now.minute
	lastdigit = int(repr(minutes)[-1])
	Air = 14
	if ( lastdigit > 6):
		GPIO.output(Air, GPIO.LOW)
	else:
        	GPIO.output(Air, GPIO.HIGH)
def waterit():
        threading.Timer(3600, waterit).start()
        SwitchLow = 5
        #SwitchMid = 6
        #SwitchHigh = 13
        global FloodTime
        global NextFloodTime
        Pump = 15
	now = datetime.datetime.now()
	NextFloodTime = now + datetime.timedelta(hours = 1, minutes = 00)
	FloodTime = now.strftime('%H:%M:%S')
	NextFloodTime = NextFloodTime.strftime('%H:%M:%S')
	if (GPIO.input(13) == 0):
        	GPIO.output(Pump, GPIO.LOW)     #Pump on

def StopPump(SwitchHigh):
	#SwitchLow = 5
        #SwitchMid = 6
        SwitchHigh = 13
	if (GPIO.input(13) == 1):
		GPIO.output(Pump, GPIO.HIGH)     #Pump off

def lightit(TurnOn, TurnOff):
  	now = datetime.datetime.now()
 	LightPin = 20
	if (now >= TurnOn and now <= TurnOff):	
		GPIO.output(LightPin, GPIO.LOW)
	else:
        	GPIO.output(LightPin, GPIO.HIGH)


def readsensors():
    ################
    #              #
    # read sensors #
    #              #
    ################
    threading.Timer(5, readsensors).start()
    global Temp0
    global Temp1
    global Moist0
    global Moist1
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

    Temp0 = TempSensors()[0]
    Temp1 = TempSensors()[1]
    Moist0 = DigitH2o(0)[2]
    Moist1 = DigitH2o(1)[2]
    pHSens = atlas_i2c()        # creates the I2C port object for pH sensor
    spi = spidev.SpiDev()       # create SPI ports for Analog to Digital Converter
    spi.open(0,0)               # set port for reading
    try:
    	OldpH = pH
    except:
        OldpH = "0"
    try:
    	pH = round(float(pHSens.query('R')), 3)
    except ValueError:
	pH = OldpH
    pass
    Pump = 15
    Air = 14
    Light = 20
    SwitchLow = 5
    SwitchMid = 6
    SwitchHigh = 13
    LightStatus = GPIO.input(Light)
    PumpStatus = GPIO.input(Pump)
    AirStatus = GPIO.input(Air)

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

    with open('/var/www/GTTrig.log', 'r') as myfile:
	MoistTrig = int(re.sub('[^0-9]','', (myfile.read())))        
    myfile.close()

    return Temp0, Temp1, Moist0, Moist1, pH, MoistTrig, Light, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, TankLevel



########################################################################################################$##################
#                                                                                                                         #
#                                                               Main                                                      #
#                                                                                                                         #
###########################################################################################################################

GPIO.setmode(GPIO.BCM)      # set GPIO to board numbering
GPIO.setwarnings(False)
Pump = 15                  #Pump control is on pin 15 of the GPIO Header
Light = 20                 #Light control is on pin 15 of the GPIO Header
Fan = 21                   #Fan  control is on pin 15 of the GPIO Header
Air = 14
BedSel = 18
SwitchLow = 5
SwitchMid = 6
SwitchHigh = 13
channel = 0
GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(Light, GPIO.OUT)
GPIO.setup(Air, GPIO.OUT)
GPIO.setup(BedSel, GPIO.OUT)
GPIO.setup(SwitchHigh, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(SwitchMid, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(SwitchLow, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

LevelL = "off"
LevelM = "off"
LevelH = "off"
TankLevel = 0
filled = 0
Draining = 0
if ( len(sys.argv) - 1 == 1 ):
	Cycle = sys.argv[1]
else:
#        Cycle = raw_input("Vegetative or Flowering : ? ")	
	 Cycle = "f"
now = datetime.datetime.now()

if (Cycle == "V" or Cycle == "v" or Cycle == "-V" or Cycle == "-v"):
        TurnOn = now.replace(hour=5, minute=30, second=0)
        TurnOff = now.replace(hour=22, minute=30, second=0)
elif (Cycle == "F" or Cycle == "f" or Cycle == "-F" or Cycle == "-f"):
        TurnOn = now.replace(hour=8, minute=00, second=0)
        TurnOff = now.replace(hour=20, minute=00, second=0)
else:
        " ok exiting "
        sys.exit()

now = now.strftime('%H:%M:%S')
os.system('clear')
print now
print "GrowBot 3"
print ""

Plotly_setup()
TankLevel = 0
readsensors()
printit(Temp0, Temp1, Moist0, Moist1, pH, MoistTrig, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, TankLevel)
plotit()
waterit()
GPIO.add_event_detect(SwitchHigh, GPIO.FALLING, callback=StopPump, bouncetime=2000)
#GPIO.add_event_detect(SwitchMid, GPIO.BOTH, callback=readsensors, bouncetime=200)
#GPIO.add_event_detect(SwitchLow, GPIO.BOTH, callback=readsensors, bouncetime=200)
while True:
	lightit(TurnOn, TurnOff)
   	AeroPump()
   	printit(Temp0, Temp1, Moist0, Moist1, pH, MoistTrig, LightStatus, LightStatusTxt, PumpStatus, PumpStatusTxt, LevelH, LevelM, LevelL, TankLevel)
   	time.sleep(3)

