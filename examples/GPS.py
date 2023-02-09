from machine import Pin, UART
from time import sleep
from micropyGPS import MicropyGPS

gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
my_gps = MicropyGPS()
    
while True:
    
    #maj donnees GPS
    for x in str(gpsModule.readline()):
        my_gps.update(x)
    
    print( "latitude", my_gps.latitude)
    print( "longitude", my_gps.longitude)
    print()

    sleep(1)
