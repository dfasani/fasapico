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
r = urequests.get("http://icam.fr")
print(r.status_code) #affiche le statut de la reponse

r = urequests.get("http://icam.fr/laPageQuiNexistePas")
print(r.status_code) #affiche le statut de la reponse



r.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!