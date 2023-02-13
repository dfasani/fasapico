from machine import Pin,PWM
from time import sleep

servo = PWM(Pin(7)) # servo motor attached PIN 7
servo.freq(50)      # 50 Hz is a good frequency

BABORD = 3000
BARRE_AU_CENTRE = 5000
TRIBORD = 9000

servo.duty_u16(BARRE_AU_CENTRE)
sleep(1)

servo.duty_u16(BABORD)
sleep(1)

servo.duty_u16(BARRE_AU_CENTRE)
sleep(1)

servo.duty_u16(TRIBORD)
sleep(1)

servo.duty_u16(BARRE_AU_CENTRE)
print("Je reste cap au centre !")
