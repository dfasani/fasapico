# -*- coding:utf-8 -*-
from bmm150 import *
from time import sleep

compasNumerique = bmm150_I2C()

#initialisation du compas numérique
while compasNumerique.ERROR == compasNumerique.sensor_init():
    print("sensor init error, please check wiring") 
    sleep(1)
    
while True:
  #lecture du cap 
  degree = compasNumerique.get_compass_degree() 

  #affichage
  print("the angle between the pointing direction and north is: %.2f "%degree) 
  
  sleep(1)
