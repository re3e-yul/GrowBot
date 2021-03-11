import os
import utime
from machine import UART, Pin, Timer
led = Pin(25, Pin.OUT)
TempSensor = machine.ADC(4)
relay1 = Pin(21, Pin.OUT)
relay2 = Pin(20, Pin.OUT)
relay3 = Pin(10, Pin.OUT)
Status = 0
Status_str =""
conversion_factor = 3.3 / (65535)
print(os.uname())

led.value(0)     # onboard LED OFF for 0.5 sec
utime.sleep(0.5)
led.value(1)

#print uart info
#uart = machine.UART(1)
uart = machine.UART(0, baudrate=300, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1)
print(uart)
print (dir(uart))
#uart.write("hello")
utime.sleep(0.5)
relay1.value(1)
relay2.value(1)
relay3.value(1)
while 1:
    led.toggle()
    
    
    while uart.any():
        led.on()
        value = str(uart.readline().strip())
        value = value.strip("'b'")
        
        now = utime.localtime()
        print (str(now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]))
        if value == "V0":
            print ("Value :", value)
            relay1.value(1)
            relay2.value(1)
            relay3.value(1)
            led.off()
            uart.write("V0")
            #utime.sleep(0.2)
            
            
        if value == "V1":
            print ("Value :", value)
            relay1.value(0)
            relay2.value(1)
            relay3.value(1)
            led.off()
            t_end = utime.time() + 10
            while utime.time() < t_end:
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                #utime.sleep(1)
            uart.write("V1")
            Status = value
        if value == "V2":
            print ("Value :", value)
            relay1.value(0)
            relay2.value(0)
            relay3.value(1)
            led.off()
            t_end = utime.time() + 13
            while utime.time() < t_end:
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.off()
                #utime.sleep(1)
            uart.write("V2")
            Status = value
        if value == "V3":
            print ("Value :", value)
            led.off()
            relay1.value(0)
            relay2.value(0)
            relay3.value(0)
            t_end = utime.time() + 13
            while utime.time() < t_end:
                
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.toggle()
                utime.sleep(0.2)
                led.off()
                utime.sleep(1)
            uart.write("V3")
            Status = value
        if value == "Vs" or value =="VS":
            if not relay1.value():
                Status_str = str(Status) + "-On"
            else:
                Status_str = str(Status) + "-Off"
            uart.write(str(Status_str))
        if value == "Vt" or value =="VT":
            reading = TempSensor.read_u16() * conversion_factor
            temperature = round((27 - (reading - 0.706)/0.001721),2)
            temperature = str(temperature) + "C"
            print(temperature)
            uart.write(temperature)
            
        if value == "Vq" or value =="VQ":
            print ("Exit")
            utime.sleep(5)
            exit()
        print ("")
        print ('relay1: ' + str(not relay1.value()))
        print ('relay2: ' + str(not relay2.value()))
        print ('relay3: ' + str(not relay3.value()))
    #utime.sleep(0.5)
    #print ("loop")
print()
print("- bye -")