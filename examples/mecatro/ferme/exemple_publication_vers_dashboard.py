# exemple_publication_vers_dashboard.py
# Exemple de publication ponctuelle vers le Dashboard public de la ferme
# Format JSON normalisé (4 champs) avec horodatage NTP pour Raspberry Pi Pico W

import json
from fasapico import *

# ==========================================
# 1. CONNEXION WI-FI & SYNCHRONISATION NTP
# ==========================================
print("Connexion au réseau Wi-Fi...")
ip = connect_to_wifi()
print(f"Wi-Fi connecté ! Adresse IP : {ip}")

# Synchronisation de l'horloge interne avec le serveur de temps NTP (indispensable pour l'horodatage)
sync_time()

# ==========================================
# 2. CONNEXION AU BROKER MQTT
# ==========================================
CLIENT_ID = "monPrenomMonNom"  # Remplace par ton prénom/nom ou nom de projet
BROKER_SERVER = "mqtt.dev.icam.school"

print(f"Connexion au Broker : {BROKER_SERVER}...")
clientMQTT = MQTTClientSimple(client_id=CLIENT_ID, server=BROKER_SERVER, ssl=True)
clientMQTT.connect()
print("Connecté au broker MQTT.")

# ==========================================
# 3. STRUCTURATION DU MESSAGE JSON (4 CHAMPS OBLIGATOIRES)
# ==========================================
# Topic public : bzh/mecatro/dashboard/<NOM_PROJET>/<NOM_VARIABLE>
TOPIC = "bzh/mecatro/dashboard/miamconnect/eau"

donnees = {
    "valeur": 12.4,                  # Mesure réelle (int, float, bool ou string)
    "unite": "cl",                   # Unité physique lisible
    "type": "float",                 # Type informatique ("int", "float", "bool", "string")
    "dateheure": get_iso_timestamp() # Horodatage ISO 8601 UTC (ex: "2026-08-28T15:21:00Z")
}

payload_json = json.dumps(donnees)

# ==========================================
# 4. PUBLICATION ET DÉCONNEXION
# ==========================================
print(f"Publication sur {TOPIC} : {payload_json}")
clientMQTT.publish(topic=TOPIC, msg=payload_json)

clientMQTT.disconnect()
print("Message envoyé et déconnexion réussie !")