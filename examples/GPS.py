from machine import *
from time import *
from micropyGPS import *

gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
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
