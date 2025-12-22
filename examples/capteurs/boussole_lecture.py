# -*- coding:utf-8 -*-
from fasapico import *
from time import *

# Initialisation du compas numérique
# Valeur par défaut sda=0, scl=1
boussoleGrove = Boussole()

while boussoleGrove.ERROR == boussoleGrove.sensor_init():
    print("sensor init error, please check wiring")
    sleep(1)

while True:
    # Lecture du cap
    cap = boussoleGrove.get_compass_degree()
    
    # Avec un f-string on peut intégrer la conversion en entier avec le formatage {cap:.0f}
    print(f"the angle between the pointing direction and north is: {cap:.0f}")
    
    sleep(1)
