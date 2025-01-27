from fasapico import *
from time import *

# Création des moteurs
moteur_a = Moteur(broche_in1=11, broche_in2=12, broche_pwm=13, vitesse=50000)
moteur_b = Moteur(broche_in1=9, broche_in2=10, broche_pwm=8, vitesse=50000)
moteur_c = Moteur(broche_in1=6, broche_in2=5, broche_pwm=7, vitesse=50000)
moteur_d = Moteur(broche_in1=4, broche_in2=3, broche_pwm=2, vitesse=50000)


# Création d'une voiture
ma_voiture = Voiture(moteur_a, moteur_b, moteur_c, moteur_d)

print("Avant")
ma_voiture.definir_vitesse(60000)
ma_voiture.avancer()
sleep(5)

print("Stop")
ma_voiture.stop()
sleep(2)

print("Differentiel droit")
ma_voiture.differentiel(traingauche=100, traindroit=90)
sleep(10)

print("Stop")
ma_voiture.stop()
sleep(2)

print("Differentiel gauche")
ma_voiture.differentiel(traingauche=70, traindroit=100)
sleep(10)

print("rotation gauche")
ma_voiture.differentiel(traingauche=-100, traindroit=100)
sleep(10)

print("Stop")
ma_voiture.stop()
sleep(2)
