from GroveUltrasonicRanger import get_distance
from utime import sleep

print("C'est parti !")

while True:
    distanceLue = get_distance(pin_number=1) #le capteur est branché sur la broche n° 1
    print("The distance from object is", distanceLue, "cm")
    sleep(0.2)
