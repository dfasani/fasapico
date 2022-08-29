from machine import Pin, PWM, ADC
import time 

led = PWM(Pin(25))
adc = ADC(Pin(27))

led.freq(1000)

while True:
    duty = adc.read_u16()
    print(duty)
    led.duty_u16(duty)
    time.sleep(.1)        #this nap is mandatory
