import machine, utime
 
analog_value = machine.ADC(27)
 
while True:
    reading = analog_value.read_u16()   #value between [0-65535]  
    print("ADC: " + str(reading))
    utime.sleep(0.2)                    #do not read to frequentrly
