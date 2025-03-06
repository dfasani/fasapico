from grove_lcd_i2c import *

#screen init
lcd = Grove_LCD_I2C()

#erase the screen
lcd.clear()

#goes to coordinates (0,0 = first line, first column)
lcd.home()
lcd.write("     David  \n     Fasani")
