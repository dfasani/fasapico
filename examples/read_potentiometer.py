from time import *
from machine import *
 
adc = ADC(27) #use the CAN on Pin 27
 
while True:
    reading = adc.read_u16()   #value between [0-65535]  
    print("ADC: " + str(reading))
    sleep(0.2)     #do not read to frequentrly
