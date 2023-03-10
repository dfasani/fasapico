from machine import Pin
import utime

def get_distance(pin_number):
    
    Pin(pin_number, Pin.OUT).low()
    utime.sleep_us(2)
    Pin(pin_number, Pin.OUT).high()
    utime.sleep_us(5)
    Pin(pin_number, Pin.OUT).low()
    
    signaloff = 0
    signalon = 0
    
    while Pin(pin_number, Pin.IN).value() == 0:
        signaloff = utime.ticks_us()
    while Pin(pin_number, Pin.IN).value() == 1:
        signalon = utime.ticks_us()
    
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    
    return distance

#how to use it
#from GroveUltrasonicRanger import get_distance
#while True:
#    distanceLue = get_distance(pin_number=27)
#    print("The distance from object is", distanceLue, "cm")
#    utime.sleep(0.2)
