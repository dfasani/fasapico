#
# Connection au reseau WiFi
#

import network
#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

print("Quel est le code postal ?")
#recuperer le code postal avec la fonction input()
#...

#
# Faire une requete vers zippopotamus
#

import urequests
url = "https://api.zippopotam.us/fr/"+postalCode
r = urequests.get(url)
#recuperer le corps de la reponse
#...
#ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
#...

import json
data = json.loads(corps)

#extraire lat
#...
#extraire lon
#...

print("Recherche de la météo aux coordonnées",lat,lon)

#
# Faire une requete vers open-meteo
#

url = "https://api.open-meteo.com/v1/forecast?latitude="+lat+"&longitude="+lon+"&current_weather=true"
#print(url)
#appeler urequests.get()
#...

#recuperer le corps de la reponse
#...
# ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!

#charger les données
data = json.loads(corps)

#extraire temperature
#temperature = data['current_weather']['temperature']
#extraire windspeed
#...
#extraire winddirection
#...


#afficher temperature
#...
#afficher windspeed
#...
#afficher winddirection
#...
