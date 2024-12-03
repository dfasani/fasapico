# -*- coding:utf-8 -*-
from bmm150 import *
from time import *

#initialisation du compas numérique
#valeur par defaut sda=0, scl=1
compasNumerique = bmm150_I2C()

while compasNumerique.ERROR == compasNumerique.sensor_init():
    print("sensor init error, please check wiring") 
    sleep(1)
    
while True:
  #lecture du cap 
  degree = compasNumerique.get_compass_degree() 

  #affichage
  print("the angle between the pointing direction and north is:  " + str(int(degree))) 
  
  sleep(1)
