from machine import Pin
import utime

def get_distance(pin_number):
    
    Pin(pin_number, Pin.OUT).low()
    utime.sleep_us(2)
    Pin(pin_number, Pin.OUT).high()
    utime.sleep_us(5)
    Pin(pin_number, Pin.OUT).low()
    
    while Pin(pin_number, Pin.IN).value() == 0:
        signaloff = utime.ticks_us()
    while Pin(pin_number, Pin.IN).value() == 1:
        signalon = utime.ticks_us()
    
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    
    return distance

while True:
    print("The distance from object is", get_distance(pin_number=7), "cm")
    utime.sleep(0.2)
