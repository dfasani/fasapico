from machine import Pin, ADC
from bluetooth import BLE
from ble import BLESimplePeripheral
import binascii
from time import sleep

# Create a Pin object for the onboard LED, configure it as an output
led = Pin("LED", Pin.OUT)
led.on()

# Define a callback function to handle received data
def on_rx(data):
    print("Data received: ", data)  # Print the received data
        
    if "LED0" in data :
        led.off()
    elif "LED1" in data :
        led.on()
                 
# Create an instance of the BLESimplePeripheral class with the BLE object
bluetoothLowEnergy = BLE()
sp = BLESimplePeripheral(ble=bluetoothLowEnergy, name="papamobile")
sp.on_write(on_rx)  # Set the callback function for data reception

#extract and prints the MAC address
mac_bytes = bluetoothLowEnergy.config('mac')[1]
mac_str = binascii.hexlify(mac_bytes).decode()
print("adresse MAC" , mac_str)

#temp sensor setup
temp_sensor = machine.ADC(4)
conversion_factor = 3.3 / (65535)
 

# Start an infinite loop
while True:
    if sp.is_connected():
        
        #temp reading and conversion
        reading = temp_sensor.read_u16() * conversion_factor 
        tempDeg = 27 - (reading - 0.706)/0.001721

        #data formating and sending
        data = "[T"+str(tempDeg) + "]"
        print("TX", data)
        sp.send(data)
        
        
        sleep(1)

