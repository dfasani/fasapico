from machine import *
from time import *

servo = PWM(Pin(7) , freq=50) # servo motor attached PIN 7 , 50 Hz is a good frequency

#valeurs a changer si besoin dans la gamme [0 , 65535]
BABORD = 3000
BARRE_AU_CENTRE = 5000
TRIBORD = 7000

print("Au centre")
servo.duty_u16(BARRE_AU_CENTRE)
sleep(1)

print("babord")
servo.duty_u16(BABORD)
sleep(1)

print("Au centre")
servo.duty_u16(BARRE_AU_CENTRE)
sleep(1)

print("tribord")
servo.duty_u16(TRIBORD)
sleep(1)

print("Au centre")
servo.duty_u16(BARRE_AU_CENTRE)
