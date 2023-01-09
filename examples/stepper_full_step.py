from machine import Pin
from time import sleep

pins = [
        Pin(2,Pin.OUT),
        Pin(3,Pin.OUT),
        Pin(4,Pin.OUT),
        Pin(5,Pin.OUT)
    ]

full_step_sequence = [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ]

while True :
    for step in full_step_sequence: # pour chacune des etapes
        for i in range(4): 			# i de 0 à 3
            pins[i].value(step[i])	# maj PIN n° i
        sleep(0.002)				# il faut attendre un peu pour laisser le temps au moteur de deplacer