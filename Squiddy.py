#!/usr/bin/python
# Import required libraries
import sys
import getopt
import time
import datetime
import RPi.GPIO as GPIO
import pH
GPIO.setmode(GPIO.BCM)
pHm = 13
pHp = 19
vega = 26
vegb = 21
floa = 20
flob = 16
AirPump = 14
Pump = 15
BedEnable = 17
GPIO.setwarnings(False)
GPIO.setup( pHp, GPIO.OUT)
GPIO.setup( pHm, GPIO.OUT)
GPIO.setup( vega, GPIO.OUT)
GPIO.setup( vegb, GPIO.OUT)
GPIO.setup( floa, GPIO.OUT)
GPIO.setup( flob, GPIO.OUT)
GPIO.setup( AirPump, GPIO.OUT)
GPIO.setup( Pump, GPIO.OUT)
GPIO.setup( BedEnable, GPIO.OUT)
def main(argv):
	selection = ''	
	volume = ''
	try:
		opts, args = getopt.getopt(argv,"s:v:",["Select=","volume="])
	except getopt.GetoptError:
		print 'test.py -s <Suplement Select> -v <Volume>'
	      	sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
        		print 'test.py -s <Suplement Select> -v <Volume>'
	         	sys.exit()
      		elif opt in ("-s", "--select"):
         		selection = arg
	      	elif opt in ("-v", "--volume"):
        	 	volume = float(arg)
	DripT = (volume * 8.2 / 10) + ( volume / 20)
	if (DripT ):
		
		
		GPIO.output(AirPump, GPIO.HIGH)
		GPIO.output(BedEnable, GPIO.LOW)
		GPIO.output(Pump, GPIO.HIGH)
		print 'AirPump Started'
		print 'Tank Cycle Started'
		print 'Preparing', volume, 'mL of', selection
		
		if (selection == "floa"):
        		GPIO.output(floa, GPIO.HIGH)
	                time.sleep(DripT)
	                GPIO.output(floa, GPIO.LOW)
     		elif (selection == "flob"):
        		GPIO.output(flob, GPIO.HIGH)
	                time.sleep(DripT)
        	        GPIO.output(flob, GPIO.LOW)
	      	elif (selection == "vega"):
        	  	GPIO.output(vega, GPIO.HIGH)
                	time.sleep(DripT)
	                GPIO.output(vega, GPIO.LOW)
       		elif (selection == "vegb"):
                	GPIO.output(vegb, GPIO.HIGH)
	                time.sleep(DripT)
        	        GPIO.output(vegb, GPIO.LOW)
	      	elif (selection == "phm") or (selection == "pHm"):
        	        GPIO.output(pHm, GPIO.HIGH)
                	time.sleep(DripT)
	                GPIO.output(pHm, GPIO.LOW)
		elif (selection == "php") or (selection == "pHp"):
                	GPIO.output(pHp, GPIO.HIGH)
	                time.sleep(DripT)
        	        GPIO.output(pHp, GPIO.LOW)


if __name__ == "__main__":
   main(sys.argv[1:])
