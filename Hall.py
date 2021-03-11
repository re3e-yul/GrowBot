#!/usr/bin/env python
#!/usr/bin/env python
import time
import serial
import sys

ser = serial.Serial(
        port='/dev/ttyAMA0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 300,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)


value = ser.readline()
while not str(value):
	value = ser.readline()
print (value)
