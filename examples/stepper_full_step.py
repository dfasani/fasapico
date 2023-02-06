from machine import Pin
from time import sleep_ms

pins = [
        Pin(2,Pin.OUT),
        Pin(3,Pin.OUT),
        Pin(4,Pin.OUT),
        Pin(5,Pin.OUT)
    ]

steps_sequence = [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ]

while True :
    for step in steps_sequence:             # pour chacune des etapes
        for i in range(10,14):# i de 11 à 14
            pins[i].value(step[i])	        # maj PIN n° i
        sleep_ms(5)			        # il faut attendre un peu pour laisser le temps au moteur de deplacer
