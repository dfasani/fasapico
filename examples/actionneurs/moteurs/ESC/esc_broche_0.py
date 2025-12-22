from machine import Pin, PWM
from time import sleep

# Configuration de la broche PWM sur la broche 0
pwm = PWM(Pin(0) , freq=50) # Fréquence standard pour les ESC (50 Hz)

# Définition des cycles de service correspondant à 1 ms et 2 ms
MIN_DUTY = 1000  # Correspond à environ 1 ms
MAX_DUTY = 9000  # Correspond à environ 2 ms

# Calibration de l'ESC
pwm.duty_u16(MAX_DUTY)  # Signal max
sleep(2)                # Attente de 2 secondes

pwm.duty_u16(MIN_DUTY)  # Signal min (arrêt)
sleep(2)                # Attente de 2 secondes


pwm.duty_u16(2000)
sleep(2)

pwm.duty_u16(3000)
sleep(2)

pwm.duty_u16(5000)
sleep(2)

pwm.duty_u16(7000)
sleep(2)

pwm.duty_u16(MAX_DUTY)
sleep(2)

pwm.duty_u16(5000)
sleep(2)

pwm.duty_u16(MIN_DUTY)
