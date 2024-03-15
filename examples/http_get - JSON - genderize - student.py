from fasapico import *
import network

#
# 1. Je me connecte au WiFi     change si necessaire
#

ip = connect_to_wifi("icam_iot", "Summ3#C@mp2022")
print(ip)

#
# 2. J'envoie une requete
#
urlGenderize = "https://api.genderize.io/?name=David"
print(urlGenderize)
jsonData = get_json_from_url(urlGenderize)

#
# 3. J'explore le résultat
#

print(jsonData) #tout afficher

