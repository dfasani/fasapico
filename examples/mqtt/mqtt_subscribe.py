import time
from fasapico import *

# Callback : fonction appelée automatiquement à chaque réception d'un message
def on_message_callback(topic, msg):
    print(f"Message reçu >> Topic : {topic} | Contenu : {msg}")

# Initialisation du client MQTT (gère aussi la connexion WiFi et la résilience)
clientMQTT = ClientMQTT(
    broker="mqtt.dev.icam.school",
    wifi_ssid="icam_iot",
    wifi_password="Summ3#C@mp2022",
    topic_cmd="bde/americam",
    callback=on_message_callback
)
clientMQTT.check_connection()

print()
print("Abonné au topic : bde/americam")

# Message pour indiquer comment quitter le script proprement
print("En attente des messages... Appuyez sur Ctrl+C pour quitter.")

# Boucle principale pour attendre les messages
while True:
    # check_msg() vérifie la boîte aux lettres de messages (non bloquant)
    clientMQTT.check_msg()
    time.sleep(0.1)
    
    # n'ajoute pas de code ici stp --> c'est la fonction on_message_callback() qu'on va completer
    # si tu n'as pas pris en compte ma consigne et que tu m'appelle je vais doubler tes frais de vie :)