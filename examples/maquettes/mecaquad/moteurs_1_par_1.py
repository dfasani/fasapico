from fasapico import *
from time import *

# Création des moteurs
moteur_a = Moteur(broche_in1=11, broche_in2=12, broche_pwm=13, vitesse=50000)
moteur_b = Moteur(broche_in1=9, broche_in2=10, broche_pwm=8, vitesse=50000)
moteur_c = Moteur(broche_in1=6, broche_in2=5, broche_pwm=7, vitesse=50000)
moteur_d = Moteur(broche_in1=4, broche_in2=3, broche_pwm=2, vitesse=50000)

while True : 
    print("A")
    moteur_a.avant()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()
    sleep(2)

    print("B")
    moteur_a.stop()
    moteur_b.avant()
    moteur_c.stop()
    moteur_d.stop()
    sleep(2)


    print("C")
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.avant()
    moteur_d.stop()
    sleep(2)


    print("D")
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.avant()
    sleep(2)

    print("STOP")
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

