from machine import *
from time import *
from micropyGPS import *
from libs.fasapico import *

#micropyGPS disponible ici : https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py

# délai d'une seconde avant l'initialisation
sleep(1)  

# Initialisation du compas numérique (par défaut sdaPin=0 , sclPin=1)
compasNumerique = bmm150_I2C(  sdaPin=26 , sclPin=27)

moduleGPS = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
gpsDecoder = MicropyGPS()
    
while True:
    
    #maj donnees GPS
    for x in str(moduleGPS.readline()):
        gpsDecoder.update(x)
        
    # Lecture des coordonnées GPS actuelles
    latitude  = gpsDecoder.latitude[0]  + gpsDecoder.latitude[1]  / 60
    longitude = gpsDecoder.longitude[0] + gpsDecoder.longitude[1] / 60
    
     # Lecture du cap (direction)
    degree = compasNumerique.get_compass_degree()

    # Affichage des données
    print( f"latitude {latitude:.6f}°\tlongitude {longitude:.6f}°\tcap {degree:3.0f}°")

    sleep(1)
