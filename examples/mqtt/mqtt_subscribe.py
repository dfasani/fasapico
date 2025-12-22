from fasapico import *

# Connexion au WiFi
ip = connect_to_wifi(ssid = "icam_iot" , password = "Summ3#C@mp2022")
print(f"Connecté au WiFi avec l'ip {ip}")

# Callback : fonction appelée automatiquement à chaque réception d'un message
def on_message_callback(topic, msg):
    print(f"Message reçu >> Topic : {topic} | Contenu : {msg}")

# Initialisation du client MQTT (remplacer `tonPrenomTonNomIci` par un identifiant unique)
clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="mqtt.dev.icam.school")
clientMQTT.connect()
clientMQTT.set_callback(on_message_callback)
clientMQTT.subscribe("bde/americam")

print()
print("Abonné au topic : bde/americam")

# Message pour indiquer comment quitter le script proprement
print("En attente des messages... Appuyez sur Ctrl+C pour quitter.")

# Boucle principale pour attendre les messages
while True:
    clientMQTT.wait_msg()
    #n'ajoute pas de code ici stp --> c'est la fonction on_message_callback() qu'on va completer
    #si tu n'as pas pris en compte ma consigne et que tu m'appelle je vais doubler tes frais de vie :)