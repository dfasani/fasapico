from machine import Pin
import utime
import time

class GroveUltrasonicRanger:
    def __init__(self, pin):
        self.pin = pin

    def get_distance(self):
        Pin(self.pin, Pin.OUT).low()
        utime.sleep_us(2)
        Pin(self.pin, Pin.OUT).high()
        utime.sleep_us(5)
        Pin(self.pin, Pin.OUT).low()
        
        signaloff = 0
        signalon = 0
        
        pin_obj = Pin(self.pin, Pin.IN)
        
        # Timeout handling to prevent infinite loop
        timeout = utime.ticks_us() + 50000 # 50ms timeout
        
        while pin_obj.value() == 0:
            signaloff = utime.ticks_us()
            if utime.ticks_us() > timeout: return 0
            
        while pin_obj.value() == 1:
            signalon = utime.ticks_us()
            if utime.ticks_us() > timeout: return 0
        
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        
        return distance

class FilteredUltrasonic(GroveUltrasonicRanger):
    def __init__(self, pin, size=5):
        super().__init__(pin)
        self.size = size
        self.history = []

    def get_distance(self):
        d = super().get_distance()
        if d > 0:
            self.history.append(d)
            if len(self.history) > self.size:
                self.history.pop(0)
        
        if not self.history:
            return 0
        return sum(self.history) / len(self.history)
