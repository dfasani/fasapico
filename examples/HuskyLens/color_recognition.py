from huskylens import HuskyLens
from time import sleep_ms

#default parameters values are : sdaPin=26 , sclPin=27
husky = HuskyLens("I2C") 
 
#activation du mode reconnaissance de couleur
husky.color_recognition_mode()
 
while True:
    reponseHuskyLens = husky.command_request()
    
    if len(reponseHuskyLens) > 0 :
        x 		= reponseHuskyLens[0][0]     #asbcisse du centre du carré : entre 0 (gauche) et 320 (droite)
        y 		= reponseHuskyLens[0][1]     #ordonnée du centre du carré : entre 0 (haut) et 240 (bas)
        largeur	= reponseHuskyLens[0][2] #largeur du carré
        hauteur	= reponseHuskyLens[0][3] #hauteur du carré
        
        print( "x" , x , "y" , y , "largeur" , largeur , "hauteur" , hauteur)
    
    sleep_ms(100)
