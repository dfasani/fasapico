from time import *
from fasapico import *

#screen init
lcd = Grove_LCD_I2C()

#erase the screen
lcd.clear()
sleep(1)

lcd.home()#retour en haut à gauche de l'écran
lcd.write("David")
lcd.cursor_position(0, 1) #passe a la ligne
lcd.write("Fasani")


sleep(2)


lcd.cursor_position(4, 1)#passe a la 5eme colonne, ligne 2 
lcd.write("Sax player! ")