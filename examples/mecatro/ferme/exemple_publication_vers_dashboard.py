# exemple_publication_vers_dashboard.py
# Exemple de publication ponctuelle vers le Dashboard public de la ferme
# Format JSON normalisé (4 champs) avec horodatage NTP pour Raspberry Pi Pico W

import json
from fasapico import *

# ==========================================
# 1. CLIENT MQTT
# ==========================================
# ClientMQTT gère automatiquement le Wi-Fi, l'heure NTP et la connexion MQTT
clientMQTT = ClientMQTT()

# ==========================================
# 2. STRUCTURATION DU MESSAGE JSON (4 CHAMPS OBLIGATOIRES)
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