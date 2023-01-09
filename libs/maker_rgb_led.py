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
    
    #type conversion
    r = int(r)
    g = int(g)
    b = int(b)
    
    #correct wrong values
    if r<0 : r=0
    if g<0 : g=0
    if b<0 : b=0
    if r>255 : r=255
    if g>255 : g=255
    if b>255 : b=255
    
    r = hex(r)[2:]
    g = hex(g)[2:]
    b = hex(b)[2:]
    
    #len correction if needed
    if len(r)==1 : r = "0"+r
    if len(g)==1 : g = "0"+g
    if len(b)==1 : b = "0"+b
    
    s = int("0x" + g + r + b) 

    # Display a pattern on the LEDs via an array of LED RGB values.
    ar = array.array("I", [0])
    
    ar[0] = int(s)
    sm.put(ar,8)
