# -*- coding:utf-8 -*-
from bmm150 import *
from time import sleep



#I2C_BUS         = 0x01   #default use I2C1
# I2C address select, that CS and SDO pin select 1 or 0 indicates the high or low level respectively. There are 4 combinations: 
ADDRESS_0       = 0x10   # (CSB:0 SDO:0)
ADDRESS_1       = 0x11   # (CSB:0 SDO:1)
ADDRESS_2       = 0x12   # (CSB:1 SDO:0)
ADDRESS_3       = 0x13   # (CSB:1 SDO:1) default i2c address
bmm150 = bmm150_I2C(ADDRESS_3,0,5,4)

def setup():
  while bmm150.ERROR == bmm150.sensor_init():
    print("sensor init error, please check connect") 
    sleep(1)
  bmm150.set_operation_mode(bmm150.POWERMODE_NORMAL)
  bmm150.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
  bmm150.set_rate(bmm150.RATE_10HZ)
  bmm150.set_measurement_xyz()
  
def loop():
  geomagnetic = bmm150.get_geomagnetic()
  print("mag x = %d ut    "%geomagnetic[0]) 
  print("mag y = %d ut    "%geomagnetic[1]) 
  print("mag z = %d ut    "%geomagnetic[2]) 
  degree = bmm150.get_compass_degree()
  print("the angle between the pointing direction and north is: %.2f "%degree) 
  print("\r\b\r\b\r\b\r\b\r\b\r")
  sleep(1)

if __name__ == "__main__":
  try:
    setup()
    print("setup")
    while True:
        loop()
  except(KeyboardInterrupt):
    bmm150.set_operation_mode(bmm150.POWERMODE_SLEEP)
    print("\n\n\n\n\n")

