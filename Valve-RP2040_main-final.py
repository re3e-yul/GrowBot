import os
import utime
import sys
from machine import UART, Pin, Timer

led = Pin(25, Pin.OUT)
TempSensor = machine.ADC(4)
relay1 = Pin(21, Pin.OUT)
relay2 = Pin(20, Pin.OUT)
relay3 = Pin(10, Pin.OUT)
Hall_Calibration = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)
Hall_Pump_Bed1 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)   #ok  c cccc                   
Hall_Pump_Bed2 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)
Hall_Drain_Bed1 = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)
Hall_Drain_Bed2 = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_DOWN)

global flow_Calib
global count0
global count1
global count2
global count3
global count4
global flow1
global flow2
global flow3
global flow4
global ReStr
global Status
global H1Status
global H2Status
global H3Status
global H4Status
global H5Status
Sensor = 0
count0 = 0
count1 = 0
count2 = 0
count3 = 0
count4 = 0
flow_Calib = 0
flow1 = 0
flow2 = 0
flow3 = 0
flow4 = 0
ReStr = ""
Status = ""
H1Status = ""
H2Status = ""
H3Status = ""
H4Status = ""
H5Status = ""
Status_str =""
conversion_factor = 3.3 / (65535)
print(os.uname())


def Hall_handler1(pin):
    global count0
    global count1
    global count2
    global count3
    global count4
    global flow1
    global flow2
    global flow3
    global flow4
    global ReStr
    global H1Status
    uart =machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
    if pin.value():
        #uart.write(str(pin))
        #print(pin)
        if pin is Hall_Calibration:
            Sensor = 'Calibration'
            count0 = count0 + 2.53
            flow_Calib = round(count0 / 10,4)
            ReStr = str(", Hall_Calibration: ") + str(flow_Calib) + str(" L")
            ReStr2 = str(flow_Calib) + str(" L")
            now = utime.localtime()
            #print (str(ReStr))
            #print ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr2 = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(" ") + str(ReStr2))
            ReStr = str("b'") + str(ReStr) + str("\n")
            ReStr2 = str("b'") + str(ReStr2) + str("\n")
            #uart.write(str(ReStr))
            H1Status = ReStr2
            ReStr = ""
            led.toggle()
            #utime.sleep(0.7)
            return (H1Status)

def Hall_handler2(pin):
    global count0
    global count1
    global count2
    global count3
    global count4
    global flow1
    global flow2
    global flow3
    global flow4
    global ReStr
    global H2Status
    uart =machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
    if pin.value():
        if pin is Hall_Pump_Bed1:
            now = utime.localtime()
            Sensor = 'Pump1'
            count1 = count1 + 2.53
            flow1 = round(count1 / 10,4)
            ReStr = str(", Hall_Pump1: ") + str(flow1) + str(" L")
            ReStr2 = str(str(flow1) + str(" L"))
            print (str(ReStr))
            print ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr2 = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(" ") + str(ReStr2))
            ReStr = str("b'") + str(ReStr) + str("\n")
            ReStr2 = str("b'") + str(ReStr2) + str("\n")
            #uart.write(str(ReStr))
            H2Status = ReStr2
            ReStr = ""
            led.toggle()
            #utime.sleep(0.7)
            return (H2Status)

def Hall_handler3(pin):
    global count0
    global count1
    global count2
    global count3
    global count4
    global flow1
    global flow2
    global flow3
    global flow4
    global ReStr
    global H3Status
    uart =machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
    if pin.value():
        if pin is Hall_Pump_Bed2:
            Sensor = 'Pump2'
            count2 = count2 + 2.53
            flow2 = round(count2 / 10,4)
            ReStr = str(", Hall_Pump2: ") + str(flow2) + str(" L")
            ReStr2 = str(str(flow2) + str(" L"))
            now = utime.localtime()
            DateNow = str(str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]))
            print (str(DateNow) + str(ReStr))
            ReStr = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr2 = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) +str(" ") + str(ReStr2))
            ReStr = str("b'") + str(ReStr) + str("\n")
            ReStr2 = str("b'") + str(ReStr2) + str("\n")
            #uart.write(str(ReStr))
            H3Status = ReStr2
            ReStr = ""
            led.toggle()
            #utime.sleep(0.7)
            return (H3Status)
            
def Hall_handler4(pin):
    global count0
    global count1
    global count2
    global count3
    global count4
    global flow1
    global flow2
    global flow3
    global flow4
    global ReStr
    global H4Status
    uart =machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
    if pin.value():
        if pin is Hall_Drain_Bed1:
            Sensor = 'Drain1'
            count3 = count3 + 2.53
            if count1 > 1:
                count1 = count1 - 0.73
                flow1 = round(count1 / 10,4)
            else:
                count1 = 0
                flow1 = 0
            ReStr = str(", Hall_Drain1: ") + str(flow1) + str(" L")
            ReStr2 = str(str(flow1) + str(" L"))
            now = utime.localtime()
            print (str(ReStr))
            print ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr2 = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(" ") + str(ReStr2))
            ReStr = str("b'") + str(ReStr) + str("\n")
            ReStr2 = str("b'") + str(ReStr2) + str("\n")
            #uart.write(str(ReStr))
            #utime.sleep(0.2)
            H4Status = ReStr2
            ReStr = ""
            led.toggle()
            #utime.sleep(0.7)
            return (H4Status)
            
            
def Hall_handler5(pin):
    global count0
    global count1
    global count2
    global count3
    global count4
    global flow1
    global flow2
    global flow3
    global flow4
    global ReStr
    global H5Status
    uart =machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
    if pin.value():
        if pin is Hall_Drain_Bed2:
            Sensor = 'Drain2'
            count4 = count4 + 2.53
            if count2 > 1:
                count2 = count2 - 0.73
                flow2 = round(count2 / 10,4)
            else:
                count2 = 0
                flow2 = 0
            ReStr = str(", Hall_Drain2: ") + str(flow2) + str(" L")
            ReStr2 = str(str(flow2) + str(" L"))
            now = utime.localtime()
            print ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(ReStr))
            ReStr2 = ( str(+ now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str(" ") + str(ReStr2))
            ReStr = str("b'") + str(ReStr) + str("\n")
            ReStr2 = str("b'") + str(ReStr2) + str("\n")
            #uart.write(str(ReStr))
            #utime.sleep(0.2)
            H5Status = ReStr2
            ReStr = ""
            led.toggle()
            #utime.sleep(0.7)
            return (H5Status)

Hall_Calibration.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=Hall_handler1)
Hall_Pump_Bed1.irq(trigger=machine.Pin.IRQ_RISING, handler=Hall_handler2)
Hall_Pump_Bed2.irq(trigger=machine.Pin.IRQ_RISING, handler=Hall_handler3)
Hall_Drain_Bed1.irq(trigger=machine.Pin.IRQ_RISING, handler=Hall_handler4)
Hall_Drain_Bed2.irq(trigger=machine.Pin.IRQ_RISING, handler=Hall_handler5)


uart = machine.UART(1, baudrate=115800, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1)
print(uart)
print (dir(uart))
uart.write(".\n")
uart.write("............................................\n")
uart.write(". hello, i'm a smart valve                 .\n")
uart.write(". usage: V[1-3]: for port selection        .\n") 
uart.write(".        Vt/VT : Temperature               .\n")
uart.write(".        Vs/VS : for valve and hall status .\n")
uart.write("............................................\n")
relay1.value(1)
relay2.value(1)
relay3.value(1)
while 1:
    led.toggle()
    #print ("hi")
    #uart.write("Hello my name is ....\n")
    
    while uart.any():
        led.on()
        value = (str(uart.readline().strip()))
        value = value.strip("'b'")
        #print ("Value :", value)
        #uart.write(value)
        #utime.sleep(0.2)
        now = utime.localtime()
        print (str(now[2]) + '-' + str(now[1]) + '-' + str(now[0]) + " " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + str ("   ") + str(value))
        if value == "V0":
            print ("Value :", value)
            relay1.value(1)
            relay2.value(1)
            relay3.value(1)
            led.off()
            utime.sleep(0.9)
            uart.write("V0")
            print ("")
            print ('relay1: ' + str(not relay1.value()))
            print ('relay2: ' + str(not relay2.value()))
            print ('relay3: ' + str(not relay3.value()))
             
        if value == "V1":
            print ("Value :", value)
            relay1.value(0)
            relay2.value(1)
            relay3.value(1)
            led.off()
            t_end = utime.time() + 10
            while utime.time() < t_end:
                utime.sleep(0.3)
                led.on()
                utime.sleep(0.3)
                led.off()
                #utime.sleep(1)
            uart.write("V1")
            Status = value
            print ("")
            print ('relay1: ' + str(not relay1.value()))
            print ('relay2: ' + str(not relay2.value()))
            print ('relay3: ' + str(not relay3.value()))
            
        if value == "V2":
            print ("Value :", value)
            relay1.value(0)
            relay2.value(0)
            relay3.value(1)
            led.off()
            t_end = utime.time() + 13
            while utime.time() < t_end:
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.off()
                #utime.sleep(1)
            uart.write("V2")
            Status = value
            print ("")
            print ('relay1: ' + str(not relay1.value()))
            print ('relay2: ' + str(not relay2.value()))
            print ('relay3: ' + str(not relay3.value()))
            
        if value == "V3":
            print ("Value :", value)
            led.off()
            relay1.value(0)
            relay2.value(0)
            relay3.value(0)
            t_end = utime.time() + 13
            while utime.time() < t_end:
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.toggle()
                utime.sleep(0.3)
                led.off()
                utime.sleep(1)
            uart.write("V3")
            Status = value
            print ("")
            print ('relay1: ' + str(not relay1.value()))
            print ('relay2: ' + str(not relay2.value()))
            print ('relay3: ' + str(not relay3.value()))
        
        if value == "Vs" or value =="VS":
            if not relay1.value():
                if Status:
                    Status_str = "Valve Status: " + str(Status) + "-On\n"
                else:
                    Status_str = "Valve Status: On\n"
            else:
                if Status:
                    Status_str = "Valve Status: " + str(Status) + "-Off\n"
                else:
                    Status_str = "Valve Status: Off\n"
            uart.write(str(Status_str))
        elif value == "Vs1" or value =="VS1":
                    print ("Calib Status: ",H1Status)
                    H1Statuss = str("Hall1 Status: ") + H1Status.strip("'b'") + str("\n")
                    uart.write(str(H1Statuss))
            
        elif value == "Vs2" or value =="VS2":
                if H4Status:
                    print ("Bed1 Status: ",H4Status)
                    H4Statuss = str("Bed1 Status: ") + H4Status.strip("'b'") + str("\n")
                    uart.write(str(H4Statuss))
                else:
                    print ("Bed1 Status: ",H2Status)
                    H2Statuss = str("Bed1 Status: ") + H2Status.strip("'b'") + str("\n")
                    uart.write(str(H2Statuss))
            
        elif value == "Vs3" or value =="VS3":
                if H5Status:
                    print ("Bed2 Status: ",H5Status)
                    H5Statuss = str("Bed2 Status: ") + H5Status.strip("'b'") + str("\n")
                    uart.write(str(H5Statuss))
                else:
                    print ("Bed2 Status: ",H3Status)
                    H3Statuss = str("Bed2 Status: ") + H3Status.strip("'b'") + str("\n")
                    uart.write(str(H3Statuss))

        if value == "Vt" or value =="VT":
            reading = TempSensor.read_u16() * conversion_factor
            temperature = round((27 - (reading - 0.706)/0.001721),2)
            temperature = str(temperature) # + "C"
            print(temperature)
            uart.write(temperature)
            
        if value == "Vq" or value =="VQ":
            print ("Exit")
            uart.write("Killing myself")
            utime.sleep(1.5)
            machine.reset()
        
    
        
        
        
