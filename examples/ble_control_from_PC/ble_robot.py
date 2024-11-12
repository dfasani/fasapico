import bluetooth
import time
from ble_simple_peripheral import *
from machine import Pin


ble = bluetooth.BLE()
p = BLESimplePeripheral(ble , "schumi")

def on_rx(v):  # v is what has been received
    ss = v.decode("utf-8")
    print(ss)
    

   
    
p.on_write(on_rx)


