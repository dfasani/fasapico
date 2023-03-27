def get_json_from_url(url):
    import urequests, json
    #retirer le commentaire pour debuger
    reponse = urequests.get(url)
    contenuDeLaReponse = reponse.content #recupere le corps de la reponse
    reponse.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
    
    #retirer le commentaire pour debuger
    #print(corps)
    
    data = json.loads(contenuDeLaReponse)
    return data

#
# 1. Je me connecte au WiFi
#

import network
#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

#
# 2. J'envoie une requete
#

data = get_json_from_url(url = "https://api.zippopotam.us/fr/44210")

#
# 3. J'explore le résultat
#

#print(data) #tout afficher
print( data["places"][0]["place name"] ) # je vais chercher les infos à la clé : "le 'PLACE NAME' du premier élément ('0') des 'PLACES'"
#print( data["places"][0]["longitude"] ) # je vais chercher les infos à la clé : "la 'LONGITUDE' du premier élément ('0') des 'PLACES'"
