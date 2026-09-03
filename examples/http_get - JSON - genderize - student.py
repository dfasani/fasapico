from fasapico import *

#
# 1. Je me connecte au WiFi     change si necessaire
#

ip = connect_to_wifi()
print(f"Adresse IP : {ip}")

#
# 2. J'envoie une requete
#
urlGenderize = "https://bzh.dev.icam.school/genderize?name=David"
print(urlGenderize)
jsonData = get_json_from_url(urlGenderize)

#
# 3. J'explore le résultat
#

print(jsonData) #tout afficher

