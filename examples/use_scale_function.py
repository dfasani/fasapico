from fasapico import *

# l'utilisateur donne une valeur dans l'intervale [0 , 65535]
print("Donne-moi un entier entre 0 et 65535")
valeurSaisie = int(input()) #transforme la chaine saisie par l'utilisateur en un entier

#mise a l'échelle dans l'intervalle [0,100]
valeurEntreOet100 = scale(valeurSaisie , 0 , 65535 , 0 , 100)

print( valeurSaisie , " donne " , valeurEntreOet100 , " %" )
