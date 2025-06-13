from machine import *
from time import *
from micropyGPS import *

#micropyGPS disponible ici : https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py
#pour l'utiliser, il faut le copier dans le dossier lib de votre pico

#si votre GPS est branché sur les pin 0 et 1
gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

#si votre GPS est branché sur les pin 4 et 5
#gpsModule = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

gpsDecoder = MicropyGPS()

print("Il faut aller dehors et attendre 1-3 minutes pour avoir un fix GPS")

while True:
    
    #maj donnees GPS
    for x in str(gpsModule.readline()):
        gpsDecoder.update(x)
    
    print( "latitude" + str( gpsDecoder.latitude) )
    print( "longitude"+ str( gpsDecoder.longitude) )
    print()

    sleep(1)
