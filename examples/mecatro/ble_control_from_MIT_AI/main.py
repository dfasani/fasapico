from bluetooth import *
from time import *
from ble_simple_peripheral import *
from machine import *

led = Pin("LED", machine.Pin.OUT)

ble = BLE()
sp = BLESimplePeripheral(ble , "pik")

def on_rx(data):  # data is what has been received
    texte = data.decode("utf-8")
    print(texte)
    if "LED0" in texte :
        led.off()
    elif "LED1" in texte :
        led.on()

sp.on_write(on_rx)  # Set the callback function for data reception
   
while True:
    if sp.is_connected():  # Check if a BLE connection is established
        sp.send("coucou")
        sleep(10)
