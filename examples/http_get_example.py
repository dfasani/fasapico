#
# Etape 1 : Connection au reseau WiFi
#

import network
#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.connect(WIFI_SSID, WIFI_PASSWORD)


#
# Etape 2 : Requete vers le serveur
#

import urequests
r = urequests.get("http://google.fr")
print(r.content) #affiche le corps de la reponse

r.close() # <-- ULTRA IMPORTANT : FERMER LA REQUETE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
