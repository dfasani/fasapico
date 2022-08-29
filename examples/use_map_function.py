from fasapico import *

x = 30000

#map the value x from the interval [0-65535] to the interval [0,100]
mappedValue = map(x , 0 , 65535 , 0 , 100)

print( x , "-->" , mappedValue)