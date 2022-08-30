from machine import Pin

button = Pin(9, Pin.IN, Pin.PULL_DOWN)

print("Please press the button!")

while button.value() == 0 :
    # we do nothing while the
    # button is not pressed
    pass 

print("Thank you =)")