#
# Connection au reseau WiFi
#

import network
#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.connect(WIFI_SSID, WIFI_PASSWORD)


#
# Faire une requete
#

import urequests
r = urequests.get("https://api.zippopotam.us/fr/44210")
corps = r.content #recupere le corps de la reponse
r.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!


print("Données non parsées")
print(corps)
print()

import json
data = json.loads(corps)
print("Données parsées")
print(data['places'][0]) # 0 pour la premiere ville qui correspond a ce code postal (e.g. pour 56890 il y a 3 villes)
print(data['places'][0]['place name'])
