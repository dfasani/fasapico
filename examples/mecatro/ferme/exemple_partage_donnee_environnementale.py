# exemple_partage_donnee_environnementale.py
# Exemple de publication périodique d'une mesure d'ambiance partagée
# Format JSON normalisé (4 champs), horodatage NTP, retain=True et boucle non-bloquante

import time
import json
import random
from fasapico import *

# Structure obligatoire : bzh/mecatro/ambiance/<NOM_PROJET>/<GRANDEUR>
# Grandeurs autorisées : temperature, humidite, pression, luminosite, co2, qualite_air, bruit, pluvio, vent_vitesse
TOPIC = "bzh/mecatro/ambiance/station_meteo/pression"

# Intervalle de publication (entre 5 000 ms et 10 000 ms, soit 0.1 Hz à 0.2 Hz)
INTERVALLE_MS = 5000 

# ==========================================
# 1. SYNCHRONISATION HORLOGE (NTP)
# ==========================================
# Synchronisation de l'heure UTC via NTP (connexion Wi-Fi automatique)
sync_time()

# ==========================================
# 2. CONNEXION AU BROKER MQTT
# ==========================================
clientMQTT = MQTTClientSimple()
print(f"Connexion au Broker : {clientMQTT.server} (ID: {clientMQTT.client_id})...")

try:
    clientMQTT.connect()
    print("Connecté avec succès au broker MQTT.")
except Exception as e:
    print("Erreur de connexion initiale au broker MQTT :", e)

# ==========================================
# 3. INITIALISATION DU REPÈRE TEMPOREL
# ==========================================
dernier_envoi_ms = time.ticks_ms()
print("Démarrage de la boucle de publication d'ambiance...")

# ==========================================
# BOUCLE PRINCIPALE NON-BLOQUANTE
# ==========================================
while True:
    try:
        temps_courant_ms = time.ticks_ms()
        
        # Vérification si l'intervalle est écoulé (gestion sûre des millisecondes)
        if time.ticks_diff(temps_courant_ms, dernier_envoi_ms) >= INTERVALLE_MS:
            dernier_envoi_ms = temps_courant_ms  
            
            # Simulation d'une valeur de capteur (ex: baromètre BMP280 en hPa)
            valeur_mesuree = 1013 + random.randint(-4, 4)
            
            # Structuration du message au format normalisé Mechatro Ferme (4 champs obligatoires)
            donnees_capteur = {
                "valeur": valeur_mesuree,
                "unite": "hPa",
                "type": "int",
                "dateheure": get_iso_timestamp()  # Horodatage ISO 8601 UTC
            }
            
            payload_json = json.dumps(donnees_capteur)
            
            # Publication avec retain=True obligatoire pour conserver la dernière valeur pour la communauté
            clientMQTT.publish(topic=TOPIC, msg=payload_json, retain=True)
            print(f"Données d'ambiance publiées sur {TOPIC} : {payload_json}")
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        print("Tentative de reconnexion...")
        try:
            connect_to_wifi()
            sync_time()
            clientMQTT.connect()
        except Exception as recon_err:
            print(f"Échec de la reconnexion automatique : {recon_err}")
            
    # Pause courte pour libérer du temps CPU
    time.sleep_ms(50)