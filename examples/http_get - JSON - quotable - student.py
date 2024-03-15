from fasapico import *

#
# 1. Je me connecte au WiFi
#

#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
#print("Connected to WiFi (" +ip+")")

#
# 2. J'envoie une requete
#
urlSagesse = "https://api.quotable.io/random"
print(urlSagesse)
jsonData = get_json_from_url(urlSagesse)

#
# 3. J'exploite le résultat
#
print("tout ce que je reçois :")
print(jsonData) #tout afficher
print()

print("auteur :")
print(jsonData['authorSlug'] ) #afficher l'auteur uniquement
print()

print("citation :")
print( ) #afficher la CITATION uniquement
