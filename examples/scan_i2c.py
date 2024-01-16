from machine import *

for sdaPin in range(0,20, 2 ) :
    sclPin = sdaPin+1

    devices = SoftI2C(sda=Pin(sdaPin), scl=Pin(sclPin)).scan()

    if len(devices) == 0:
        print("sdaPin:",sdaPin, "\tsclPin:" , sclPin, "\t\tNo i2c device !")
    else:
        print("sdaPin:",sdaPin, "\tsclPin:" , sclPin, '\t\ti2c devices found:',len(devices))

        for device in devices:
            print("\t|- Decimal address: ",device," | Hexa address: ",hex(device))

    print()
