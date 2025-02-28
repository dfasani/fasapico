from fasapico import *

#
# 1. Je me connecte au WiFi
#

#change si necessaire
ip = connect_to_wifi(ssid = "icam_iot", password = "Summ3#C@mp2022")
print("Connected to WiFi (" +ip+")")

#
# 2. J'envoie une requete
#
urlDemandee = "https://api.quotable.io/random"
print(urlDemandee)
jsonData = get_json_from_url(urlDemandee)

#
# 3. J'exploite le résultat
#
print("tout ce que je reçois :")
print(jsonData) #tout afficher --> tu peux supprimer cette partie
print()

print("auteur :")
print(jsonData['authorSlug'] ) #afficher l'auteur uniquement --> a remplacer par la citation uniquement
