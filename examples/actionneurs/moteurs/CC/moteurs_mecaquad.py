from fasapico import *
from time import *

# ------------------------------------------
#
# CE PROGRAMME PEUT ETRE EXECUTE EN L'ETAT
# A TOI DE LE COMPLETER POUR QU'IL 
# FONCTIONNE PARFAITEMENT !!!
#
# ------------------------------------------

# Création des moteurs
moteur_a = Moteur(broche_in1=11, broche_in2=12, broche_pwm=13, vitesse=50000)
moteur_b = Moteur(broche_in1=9, broche_in2=10, broche_pwm=8, vitesse=50000)
#TODO ajouter les autres moteurs
# c.f. le plan de cablage : https://docs.google.com/spreadsheets/d/1OXjJoho3oYTuebgcoxP1DS4oncB8VAuP2rYHh3s-rio/edit#gid=0



print("en avant vite 3 sec")
moteur_a.avant()
#TODO ajouter les autres moteurs
sleep(3)

print("stop 1 sec")
moteur_a.stop()  
#TODO ajouter les autres moteurs
sleep(1)

print("en arriere vite 2 sec")
moteur_a.arriere()
#TODO ajouter les autres moteurs
sleep(2)

print("stop 1 sec")
moteur_a.stop()  
#TODO ajouter les autres moteurs
sleep(1)

#on diminue les gaz
moteur_a.definir_vitesse(35000)
moteur_b.definir_vitesse(35000)
#TODO ajouter les autres moteurs

print("en avant lentement 5 sec")
moteur_a.avant()
#TODO ajouter les autres moteurs
sleep(5)

print("stop definitif")
moteur_a.stop()  
#TODO ajouter les autres moteurs
