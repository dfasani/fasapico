# main.py
# Exemple de publication MQTT au format JSON pour Raspberry Pi Pico W
# Cadencement non-bloquant (ticks_ms) et simulation directe de variation de capteur

import time
import json
import random  # Module pour générer du hasard
from fasapico import *

# ==========================================
# CONFIGURATION DU PROJET & MQTT
# ==========================================
CLIENT_ID = "JeanLouisSerreTech" 
BROKER_SERVER = "mqtt.dev.icam.school"
TOPIC = "bzh/mecatro/env/pression_atmospherique"

# Intervalle de temps souhaité entre chaque envoi (5000 ms = 5 secondes)
INTERVALLE_MS = 5000 

# ==========================================
# 1. CONNEXION WI-FI & BROKER MQTT
# ==========================================
print("Connexion au réseau Wi-Fi...")
ip = connect_to_wifi()  # Identifiants par défaut gérés par la bibliothèque fasapico
print(f"Wi-Fi connecté ! Adresse IP : {ip}")

print(f"Connexion au Broker : {BROKER_SERVER}...")
clientMQTT = MQTTClientSimple(client_id=CLIENT_ID, server=BROKER_SERVER, ssl=True)

try:
    clientMQTT.connect()
    print("Connecté avec succès au broker MQTT.")
except Exception as e:
    print("Erreur de connexion initiale au broker MQTT :", e)

# ==========================================
# 2. INITIALISATION DU REPERE TEMPOREL
# ==========================================
# Au démarrage, on enregistre le premier repère en millisecondes
dernier_envoi_ms = time.ticks_ms()

print("Démarrage de la boucle de publication active...")

# ==========================================
# BOUCLE PRINCIPALE NON-BLOQUANTE
# ==========================================
while True:
    try:
        # À chaque passage de boucle, on regarde quelle "heure" il est sur la Pico
        temps_courant_ms = time.ticks_ms()
        
        # On calcule l'écart entre le temps courant et le moment du dernier envoi.
        if time.ticks_diff(temps_courant_ms, dernier_envoi_ms) >= INTERVALLE_MS:
            
            # 1. On met à jour notre repère pour le prochain envoi
            dernier_envoi_ms = temps_courant_ms  
            
            # 2. Simulation de la mesure en une seule ligne de code
            valeur_mesuree = 1025 + random.randint(-3, 3)
            
            # 3. Structuration de la donnée au format JSON Mechatro BZH V2
            donnees_capteur = {
                "valeur": valeur_mesuree,
                "unite": "hPa",
                "type": "int"  # Type informatique de la donnée
            }
            
            # 4. Conversion en chaîne de caractères JSON
            payload_json = json.dumps(donnees_capteur)
            
            # 5. Publication sur le broker avec persistance (retain=True, plus sympa pour les copains ;o)
            clientMQTT.publish(topic=TOPIC, msg=payload_json, retain=True)
            print(f"Données publiées sur {TOPIC} : {payload_json}")
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        print("Tentative de reconnexion...")
        try:
            connect_to_wifi()
            clientMQTT.connect()
        except Exception as recon_err:
            print(f"Échec de la reconnexion automatique : {recon_err}")
            
    # Très courte pause (50 ms) pour soulager le processeur de la Pico
    time.sleep_ms(50)