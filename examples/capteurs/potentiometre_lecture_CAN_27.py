from time import *
from machine import *
 
adc = ADC(27) #on utilise le CAN (Convertisseur Analogique Numérique) de la broche 27
 
while True:
    valeurLue = adc.read_u16()   #valeur dans l'intervalle [0-65535]  
    print("ADC: " + str(valeurLue))
    sleep(0.1)     #il ne faut pas solliciter le CAN "trop" souvent
