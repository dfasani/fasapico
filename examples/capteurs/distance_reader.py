from fasapico import *
from machine import *
from time import *

print("Here we go !")

sensor = GroveUltrasonicRanger(pin=1) #le capteur est branché sur la broche n° 1

while True:
    distanceLue = sensor.get_distance()
    print("The distance from object is", distanceLue, "cm")
    sleep(0.2)
