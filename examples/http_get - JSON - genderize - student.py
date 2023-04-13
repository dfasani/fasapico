from fasapico import connect_to_wifi


def get_json_from_url(url):
    import urequests, json
    
    #retirer le commentaire pour debuger
    #print("Sending request to :",url)
    
    reponse = urequests.get(url)
    contenuDeLaReponse = reponse.content #recupere le corps de la reponse
    reponse.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
    
    #retirer le commentaire pour debuger
    #print(corps)
    
    jsonData = json.loads(contenuDeLaReponse)
    return jsonData

#
# 1. Je me connecte au WiFi
#

import network
#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
print(ip)

#
# 2. J'envoie une requete
#

jsonData = get_json_from_url(url = "https://api.genderize.io/?name=David")

#
# 3. J'explore le résultat
#

print(jsonData) #tout afficher

