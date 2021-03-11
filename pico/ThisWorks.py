import os
import utime
from machine import UART, Pin, Timer
led = Pin(25, Pin.OUT)
led.value(0)     # onboard LED OFF for 0.5 sec
utime.sleep(0.5)
led.value(1)
uart = machine.UART(0, baudrate=300, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1)
print(os.uname())
print(uart)
print (dir(uart))
#uart.write("hello")
utime.sleep(0.5)

while 1:
    led.toggle()
    uart.write(" hello\n")
    
    while uart.any():
        led.on()
        #value = str(uart.readline())
        value = str(uart.readline().strip())
        value = value.strip("'b'")
        
        now = utime.localtime()
        print (str(now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(value))
        