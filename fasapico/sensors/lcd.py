from machine import Pin, SoftI2C
import utime
import time
from time import *

class Grove_LCD_I2C(object):
    # Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for display/cursor shift 
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00 
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, i2c_num=0, sda_pin=4, scl_pin=5 ,address=62, oneline=False, charsize=LCD_5x8DOTS):

        #print("LCD\t\t\tidI2C" , i2c_num, "sdaPin" , sda_pin , "sclPin" ,scl_pin )

        #David : if init fails, give a 10 sec retry loop!

        timeout = utime.time() + 10 # 10 sec
        while True:
            #i2cGrove = I2C(i2c_num, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=1000)
            i2cGrove = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin),)
            if len(i2cGrove.scan()) > 0 or utime.time() > timeout:
                break

            utime.sleep_ms(100)

        self.i2c = i2cGrove
        self.address = address

        self.disp_func = self.LCD_DISPLAYON # | 0x10
        if not oneline:
            self.disp_func |= self.LCD_2LINE
        elif charsize != 0:
            # For 1-line displays you can choose another dotsize
            self.disp_func |= self.LCD_5x10DOTS

        # Wait for display init after power-on
        utime.sleep_ms(50) # 50ms

        # Send function set
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        utime.sleep_us(4500) ##time.sleep(0.0045) # 4.5ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        utime.sleep_us(150) ##time.sleep(0.000150) # 150µs = 0.15ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)

        # Turn on the display
        self.disp_ctrl = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display(True)

        # Clear it
        self.clear()

        # Set default text direction (left-to-right)
        self.disp_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.cmd(self.LCD_ENTRYMODESET | self.disp_mode)

    def cmd(self, command):
        assert command >= 0 and command < 256
        command = bytearray([command])
        self.i2c.writeto_mem(self.address, 0x80, bytearray([]))
        self.i2c.writeto_mem(self.address, 0x80, command)

    def write_char(self, c):
        assert c >= 0 and c < 256
        c = bytearray([c])
        self.i2c.writeto_mem(self.address, 0x40, c)

    def write(self, *args):
        text = ' '.join(map(str, args))  # Transforme chaque argument en chaîne et insère un espace
        new_line = False  # Variable pour suivre si on a déjà effectué un saut de ligne
        for char in text:
            if char == '\n' and not new_line:
                self.cursor_position(0, 1)
                new_line = True  # Premier saut de ligne traité
            elif char != '\n':
                self.write_char(ord(char))
                new_line = False  # Réinitialise l'état après avoir trouvé un caractère normal

    def cursor(self, state):
        if state:
            self.disp_ctrl |= self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def cursor_position(self, col, row):
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.cmd(col)

    def autoscroll(self, state):
        if state:
            self.disp_ctrl |= self.LCD_ENTRYSHIFTINCREMENT
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_ENTRYSHIFTINCREMENT
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def blink(self, state):
        if state:
            self.disp_ctrl |= self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def display(self, state):
        if state:
            self.disp_ctrl |= self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def clear(self):
        self.cmd(self.LCD_CLEARDISPLAY)
        utime.sleep_ms(2) # 2ms

    def home(self):
        self.cmd(self.LCD_RETURNHOME)
        utime.sleep_ms(2) # 2m
