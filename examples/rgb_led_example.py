from fasapico import *
import time

while True:
    print("off")
    rgbLed(0,0,0)
    time.sleep_ms(2000)
    
    print("blue")
    rgbLed(0,0,255)
    time.sleep_ms(2000)

    print("red")
    rgbLed(0,255,0)
    time.sleep_ms(2000)

    print("green")
    rgbLed(255,0,0)
    time.sleep_ms(2000)
    
    print("yellow")
    rgbLed(255,255,0)
    time.sleep_ms(2000)

    print("cyan")
    rgbLed(255,0,255)
    time.sleep_ms(2000)
    
    print("purple")
    rgbLed(0,255,255)
    time.sleep_ms(2000) 

    print("white")
    rgbLed(255,255,255)
    time.sleep_ms(2000)
