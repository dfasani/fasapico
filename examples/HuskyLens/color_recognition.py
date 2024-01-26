from huskylens import HuskyLens
from time import sleep_ms

#default parameters values are : sdaPin=26 , sclPin=27
husky = HuskyLens("I2C") 
 
#activation du mode reconnaissance de couleur
husky.color_recognition_mode()
 
while True:
    reponseHuskyLens = husky.command_request()
    
    if len(reponseHuskyLens) > 0 :
        x 		= reponseHuskyLens[0][0]
        y 		= reponseHuskyLens[0][1]
        largeur	= reponseHuskyLens[0][2]
        hauteur	= reponseHuskyLens[0][3]
        
        print( "x" , x , "y" , y , "largeur" , largeur , "hauteur" , hauteur)
    
    sleep_ms(100)
