#!/usr/bin/python
import io # used to create file streams
import fcntl # used to access I2C parameters like addresses
import time # used for sleep delay and timestamps
import sys # used for system calls 
import os
import subprocess
import re

class atlas_i2c():
	
    	long_timeout = 2.0 # the timeout needed to query readings and calibrations
    	short_timeout = 1.0 # timeout for regular commands
    	default_bus = 1 # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
    	default_address = 99 # the default address for the pH sensor
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

	def list_i2c_devices(self):
                prev_addr = self.current_addr # save the current address so we can restore it after
                i2c_devices = []
                for i in range (0,128):
                        try:
                                self.set_i2c_address(i)
                                self.read()
                                i2c_devices.append(i)
                        except IOError:
                                pass
                self.set_i2c_address(prev_addr) # restore the address we were using
                return i2c_devices


def main():

	for x in range(1,len(sys.argv)):
        	try:
                	y=sys.argv[x]
	                float(y)
        	        addr = y
	        except ValueError:
        	        verb = y

	try:
		device = atlas_i2c()     # creates the I2C port object, specify the address or bus if necessary
		if (len(sys.argv) < 3 ):
			print ''
			print 'Usage: Atlas-I2C [verb] [address] (in any order)'
			print 'verbs as in i2c Commands listed in Atlas Scientific documentation'
			print 'address as reported by i2cdetect -y [1/0] '
			print "atlas-I2C [address] will invoke 'i', information on the device at address "
			print  ""
			if (len(sys.argv) == 1):
				print 'Device(s) detected: '
				print ""
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
				print ""
                        	print ""
				exit()
			else:
				device.set_i2c_address(int(addr))
				verb = 'i'
				try:
					
                                	print "Address: ",addr, "\tInfo: ", (device.query(verb))[3:]
					Type = device.query('i')[3:5]
					if (Type == 'pH'):
						print "supported verbs: "
						print ""
						print "Baud\t\t: switch to UART : Baud,300 [300/1200/2400/9600/19200/38400/57600/115200]"
						print "Cal\t\t: perform Calibration : Cal,mid,7.00 Cal,low,4.00 Cal,high,10 Cal,Clear"
						print "Export/Import\t: Export/Import Calibration"
						print "Factory\t\t: Enable Factory reset"
						print "Find\t\t: blink led "
                                                print "i\t\t: device information : returns [device], [firmware version]"
						print "i2c\t\t: change i2c address : i2c,100" 
                                                print "L\t\t: enable/disable LED "
                                                print "Plock\t\t: enable/disable Protocol lock"
                                                print "R\t\t: return a single reading"
						print "Sleep\t\t: enter sleep mode"
						print "Slope\t\t: return the slope : Slope,?"
                                                print "Status\t\t: return status information"
                                                print "T\t\t: temperature compensation : T,? T,20.0"
					if (Type == 'EC'):
						print "supported verbs: "
                                                print ""
                                                print "Baud\t\t: switch to UART : Baud,300 [300/1200/2400/9600/19200/38400/57600/115200]"
                                                print "Cal\t\t: perform Calibration : Cal,mid,7.00 Cal,low,4.00 Cal,high,10 Cal,Clear"
                                                print "Export/Import\t: Export/Import Calibration"
                                                print "Factory\t\t: Enable Factory reset"
                                                print "Find\t\t: blink led "
                                                print "i\t\t: device information : returns [device], [firmware version]"
                                                print "i2c\t\t: change i2c address : i2c,100"
						print "K\t\t: set probe type : K,? K,0.1 K,1.0 K,10 K,n (n = any value; floating point in ASCII)"
						print "L\t\t: enable/disable LED "
						print "O\t\t: enable disale parameters : O,[EC,TDS,S,SG],[0,1]"
						print "Plock\t\t: enable/disable Protocol lock"
                                                print "R\t\t: return a single reading"
                                                print "Sleep\t\t: enter sleep mode"
                                                print "Status\t\t: return status information"
                                                print "T\t\t: temperature compensation : T,? T,20.0"
					if (Type == 'PM'):
						print "supported verbs: "
                                                print ""
                                                print "Baud\t\t: switch to UART : Baud,300 [300/1200/2400/9600/19200/38400/57600/115200]"
                                                print "Cal\t\t: perform Calibration : "
						print "D\t\t: dispense modes : D,n (n=+/-mL * for continuous) D,?"
						print "\t\t\t\t   D,n,T (n=+/-mL T=Min)"
						print "Factory\t\t: Enable Factory reset"
                                                print "Find\t\t: blink led "
                                                print "i\t\t: device information : returns [device], [firmware version]"
                                                print "i2c\t\t: change i2c address : i2c,100"
						print "L\t\t: enable/disable LED "
                                                print "O\t\t: enable disale parameters : O,[EC,TDS,S,SG],[0,1]"
						print "P\t\t: pauses the pump during dispensing"
						print "Plock\t\t: enable/disable Protocol lock"
						print "Pv\t\t: check pump voltage"
                                                print "R\t\t: return a single reading"
                                                print "Sleep\t\t: enter sleep mode"
                                                print "Status\t\t: return status information"
						print "TV,?\t\t: shows total volume dispensed"
						print "ATV,?\t\t: absolute value of the total volume dispensed "
						print "clear\t\t: clears the total dispensed volume"
                                except IOError:
                                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
				print ""
                        	print ""
				exit()
			
		elif (len(sys.argv) == 3):
			device.set_i2c_address(int(addr))
			print ""
        		print ""
			try:
				Type = device.query('i')[3:5]
				print(device.query(verb)) 
			except IOError:
        			print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
			print ""
        		print ""
			exit()

	except IOError:
                        print ""
                        print "No I2C port detected"
                        print ""
                        print ""
                        exit()




if __name__ == '__main__':
        main()

