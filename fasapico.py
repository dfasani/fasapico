from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import array


@asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT,
autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    label("bitloop")
    out(x, 1) .side(0) [T3 - 1]
    jmp(not_x, "do_zero") .side(1) [T1 - 1]
    jmp("bitloop") .side(1) [T2 - 1]
    label("do_zero")
    nop() .side(0) [T2 - 1]

# Create the StateMachine with the ws2812 program, outputting on pin GP28 (Maker Pi Pico).
sm = StateMachine(0, ws2812, freq=8000000, sideset_base=Pin(28))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# change the value of the onboard RGB Led
def rgbLed(r,g,b):
    
    #correct wrong values
    if r<0 : r=0
    if g<0 : g=0
    if b<0 : b=0
    if r>255 : r=255
    if g>255 : g=255
    if b>255 : b=255
    
    #type conversion
    r = int(r)
    g = int(g)
    b = int(b)
    
    r = hex(r)[2:]
    g = hex(g)[2:]
    b = hex(b)[2:]
    
    #len correction if needed
    if len(r)==1 : r = "0"+r
    if len(g)==1 : g = "0"+g
    if len(b)==1 : b = "0"+b
    
    s = int("0x" + r + g + b) 

    # Display a pattern on the LEDs via an array of LED RGB values.
    ar = array.array("I", [0])
    
    ar[0] = int(s)
    sm.put(ar,8)




    
# used to ensure that a value is a number
def isNumber(n):
    if not (type(n) is int or type(n) is float):
        try:
            n = float(n)
        except:
            return 0
    return n



# translates emojis to their corresponding control characters
def emojiCharacter(c):
    if c == "in-love":
        return chr(20)
    if c == "sad":
        return chr(21)
    if c == "happy":
        return chr(22)
    if c == "thinking":
        return chr(23)
    if c == "quiet":
        return chr(24)
    if c == "confused":
        return chr(25)
    if c == "suspicious":
        return chr(26)
    if c == "unhappy":
        return chr(27)
    if c == "bored":
        return chr(28)
    if c == "surprised":
        return chr(29)
    
    
# map (scale) a value x from one range [in_min, in_max] to a new range [out_min, out_max]
def map(x, in_min, in_max, out_min, out_max):
    """ Maps two ranges together """
    return int((x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min)
