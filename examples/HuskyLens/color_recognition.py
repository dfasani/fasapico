from huskylens import HuskyLens
import time

#default parameters values are : sdaPin=26 , sclPin=27,  i2cid=1
husky = HuskyLens("I2C") 
 
#activation du mode reconnaissance de couleur
husky.color_recognition_mode()
 
while True:
    result = husky.command_request()
    print(result)

    time.sleep_ms(100)
