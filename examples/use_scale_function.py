from fasapico import *

# l'utilisateur donne une valeur dans l'intervale [0 , 65535]
valeurEntreOet65535 = int(input("Donne une valeur entre [0 , 65535]"))

#mise a l'échelle dans l'intervalle [0,100]
valeurEntreOet100 = scale(valeurEntreOet65535 , 0 , 65535 , 0 , 100)

print( valeurEntreOet65535 , " donne " , valeurEntreOet100 , " %" )
