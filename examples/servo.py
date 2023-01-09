from machine import Pin,PWM
from time import sleep

servo = PWM(Pin(7)) # servo motor attached PIN 7
servo.freq(50)      # 50 Hz is a good frequency

MIN = 1000
MID = 5000
MAX = 9000

servo.duty_u16(MID)
sleep(1)

servo.duty_u16(MIN)
sleep(1)

servo.duty_u16(MID)
sleep(1)

servo.duty_u16(MAX)
sleep(1)

servo.duty_u16(MID)
