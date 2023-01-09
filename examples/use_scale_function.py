from fasapico import *

#change this value from [0 , 65535]
x = 30000

#map the value x from the interval [0-65535] to the interval [0,100]
mappedValue = scale(x , 0 , 65535 , 0 , 100)

print( x , "-->" , mappedValue)
