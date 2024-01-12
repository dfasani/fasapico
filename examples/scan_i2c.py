import machine


for pins in [ (0,0,1) , (0,4,5), (0,8,9), (0,12,13), (0,16,17), (1,2,3), (1,6,7), (1,10,11), (1,14,15), (1,18,19)]:
    i2c_id ,sdaPin, sclPin = pins

    sda=machine.Pin(sdaPin)
    scl=machine.Pin(sclPin)
    i2c=machine.I2C(i2c_id,sda=sda, scl=scl, freq=400000)

    devices = i2c.scan()

    if len(devices) == 0:
        print("i2c_id:" ,i2c_id ,"\tsdaPin:",sdaPin, "\tsclPin:" , sclPin, "\t\tNo i2c device !")
    else:
        print("i2c_id:" ,i2c_id ,"\tsdaPin:",sdaPin, "\tsclPin:" , sclPin, '\t\ti2c devices found:',len(devices))

    for device in devices:
        print("\t|- Decimal address: ",device," | Hexa address: ",hex(device))

    print()
