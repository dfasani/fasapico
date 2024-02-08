from machine import *
from time import *

#################################
#                               #
# INITIALISATION DES VARIABLES  #
#                               #
#################################

# -------------- #
# PARTIE STEPPER #
# -------------- #

pins = [
        Pin(10,Pin.OUT),
        Pin(11,Pin.OUT),
        Pin(12,Pin.OUT),
        Pin(13,Pin.OUT)
    ]

#############################
#                           #
# DEFINITION DES FONCTIONS  #
#                           #
#############################   

def runStepper(nbPas):
    
    if nbPas > 0 :
        steps_sequence = [     
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ]
        
    else:
        steps_sequence = [     
            [0,0,0,1],
            [0,0,1,0],
            [0,1,0,0],
            [1,0,0,0]
        ]
        
    
    for _ in range(abs(nbPas)):
        for step in steps_sequence:     # pour chacune des etapes
                for i in range(4):              # i de 0 à 3
                    pins[i].value(step[i])	# maj PIN n° i
                sleep_ms(5	)			# il faut attendre un peu pour laisser le temps au moteur de deplacer


######################
#                    #
# BOUCLE PRINCIPALE  #
#                    #
######################

while True :
  print("a droite")
  runStepper(30)
  
  print("a gauche")
  runStepper(-30)
