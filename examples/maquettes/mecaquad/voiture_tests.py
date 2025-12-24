from fasapico import *
from time import *

# Création des moteurs
moteur_a = Moteur(broche_in1=11, broche_in2=12, broche_pwm=13, vitesse=50000)
moteur_b = Moteur(broche_in1=9, broche_in2=10, broche_pwm=8, vitesse=50000)
moteur_c = Moteur(broche_in1=6, broche_in2=5, broche_pwm=7, vitesse=50000)
moteur_d = Moteur(broche_in1=4, broche_in2=3, broche_pwm=2, vitesse=50000)


# Création d'une voiture
ma_voiture = Voiture(moteur_a, moteur_b, moteur_c, moteur_d)

print("Avant à 50%")
ma_voiture.definir_vitesse_pourcentage(50)
ma_voiture.avancer()
sleep(2)

print("Virage différentiel à droite")
ma_voiture.piloter_differentiel(vitesse=40, direction=30)
sleep(2)

print("Demi-tour")
ma_voiture.faire_demi_tour()
sleep(1)

print("Vibration")
ma_voiture.vibrer()
sleep(1)

print("Omnidirectionnel : Diagonale Droite (45°)")
ma_voiture.piloter_omnidirectionnel(direction_deg=45, puissance=50)
sleep(2)

print("Mode Démonstration")
ma_voiture.demonstration()

print("Arrêt progressif")
ma_voiture.arreter_progressivement()
