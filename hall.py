#!/usr/bin/python
# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO

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
  if vol == 0:
 	stat = 0
  else:
	stat = 1
#  except:
#	stat = 1 
		
#  except:
#		print "V"  
#  pass
	
def main():
  
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.
#  global stat
#  stat = 0
  try:
    # Loop until users quits with CTRL-C
    #while True :
    t_end = time.time() + 1
    while time.time() < t_end:
      time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()
  try:
    print stat
  except:
    print 0
# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)
GPIO.setup(22 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.BOTH, callback=sensorCallback, bouncetime=900)

if __name__=="__main__":
   timeout = time.time() + 5

   main()
