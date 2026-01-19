from fasapico import *
from time import *

#
# CE PROGRAMME FONCTIONNE EN PARTIE SEULEMENT
#  --> A TOI DE LE CORRIGER
#

# Création des moteurs
moteur_a = Moteur(broche_in1=11, broche_in2=12, broche_pwm=13, vitesse=50000)
moteur_b = Moteur(broche_in1=9, broche_in2=10, broche_pwm=8, vitesse=50000)
moteur_c = Moteur(broche_in1=6, broche_in2=5, broche_pwm=7, vitesse=50000)
moteur_d = Moteur(broche_in1=4, broche_in2=3, broche_pwm=2, vitesse=50000)

def avancer():
    moteur_a.avant()
    moteur_b.avant()
    moteur_c.avant()
    moteur_d.avant()

def reculer():
    moteur_a.arriere()
    moteur_b.arriere()
    moteur_c.arriere()
    moteur_d.arriere()

def translation_droite():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

def translation_gauche(): 
    moteur_a.avant()
    moteur_b.arriere()
    moteur_c.arriere()
    moteur_d.avant()

def rotation_horaire():
    moteur_a.avant()
    moteur_b.arriere()
    moteur_c.avant()
    moteur_d.arriere()

def rotation_anti_horaire():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

def diagonale_avant_droite():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()
    
def diagonale_arriere_gauche():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

def diagonale_avant_gauche():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

def diagonale_arriere_droite():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

def stop():
    moteur_a.stop()
    moteur_b.stop()
    moteur_c.stop()
    moteur_d.stop()

print("Avancer")
avancer()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Reculer")
reculer()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Translation à droite")
translation_droite()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Translation à gauche")
translation_gauche()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Rotation horaire")
rotation_horaire()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Rotation anti-horaire")
rotation_anti_horaire()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Diagonale avant droite")
diagonale_avant_droite()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Diagonale arrière gauche")
diagonale_arriere_gauche()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Diagonale avant gauche")
diagonale_avant_gauche()
sleep_ms(1000)
stop()
sleep_ms(1000)

print("Diagonale arrière droite")
diagonale_arriere_droite()
sleep_ms(1000)
stop()
sleep_ms(1000)
