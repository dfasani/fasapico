from fasapico import Stepper
from time import sleep_ms

#################################
#                               #
# INITIALISATION DES VARIABLES  #
#                               #
#################################

# -------------- #
# PARTIE STEPPER #
# -------------- #

# Utilisation de la classe Stepper de la librairie fasapico
stepper = Stepper() # Pins par defaut: 10, 11, 12, 13

######################
#                    #
# BOUCLE PRINCIPALE  #
#                    #
######################

while True :
  print("a droite")
  stepper.move(-100)
  sleep_ms(500)
  
  print("a gauche")
  stepper.move(100)
  sleep_ms(500)
