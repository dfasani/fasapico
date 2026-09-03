# exemple_publication_vers_dashboard.py
# Exemple de publication périodique vers le Dashboard public de la ferme
# Format JSON normalisé (4 champs) avec horodatage NTP pour Raspberry Pi Pico W

import time
import json
import random
from fasapico import *

# Topic public : bzh/mecatro/dashboard/<NOM_PROJET>/<NOM_VARIABLE>
TOPIC = "bzh/mecatro/dashboard/miamconnect/eau"

# Intervalle de publication (ex: toutes les 5 000 ms)
INTERVALLE_MS = 5000

# ==========================================
# 1. CLIENT MQTT
# ==========================================
# ClientMQTT gère automatiquement le Wi-Fi, l'heure NTP et la connexion MQTT
clientMQTT = ClientMQTT()

# ==========================================
# 2. INITIALISATION DU REPÈRE TEMPOREL
# ==========================================
dernier_envoi_ms = time.ticks_ms()
print("Démarrage de la boucle de publication vers le Dashboard...")

# ==========================================
# 3. BOUCLE PRINCIPALE NON-BLOQUANTE
# ==========================================
while True:
    temps_courant_ms = time.ticks_ms()
    
    # Vérification si l'intervalle est écoulé
    if time.ticks_diff(temps_courant_ms, dernier_envoi_ms) >= INTERVALLE_MS:
        dernier_envoi_ms = temps_courant_ms  
        
        # Simulation d'une mesure réelle avec légère variation (ex: niveau d'eau en cl)
        valeur_mesuree = round(12.4 + random.uniform(-1.5, 1.5), 1)
        
        # Structuration du message au format normalisé Mechatro Ferme (4 champs obligatoires)
        donnees = {
            "valeur": valeur_mesuree,        # Mesure réelle (int, float, bool ou string)
            "unite": "cl",                   # Unité physique lisible
            "type": "float",                 # Type informatique ("int", "float", "bool", "string")
            "dateheure": get_iso_timestamp() # Horodatage ISO 8601 UTC
        }
        
        payload_json = json.dumps(donnees)
        clientMQTT.publish(topic=TOPIC, msg=payload_json)
        print(f"Publication sur {TOPIC} : {payload_json}")
            
    # Pause courte pour libérer du temps CPU
    time.sleep_ms(50)