from huskylens import HuskyLens
from time import sleep_ms

#default parameters values are : sdaPin=26 , sclPin=27
husky = HuskyLens("I2C") 
 
#activation du mode reconnaissance de couleur
husky.color_recognition_mode()
 
while True:
    result = husky.command_request()
    print(result)

    sleep_ms(100)
