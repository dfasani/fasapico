# exemple_telecommande_privee.py
# Exemple de télécommande / contrôle privé pour Raspberry Pi Pico W
# - Écoute des ordres actionneurs via Callback MQTT (Application -> Pico)
# - Publication des mesures capteurs privées (Pico -> Application)

import time
import json
from machine import Pin
from fasapico import *

# ==========================================
# CONFIGURATION DU PROJET & MQTT
# ==========================================
NOM_PROJET = "miamconnect"
CLIENT_ID = f"Pico_{NOM_PROJET}"
BROKER_SERVER = "mqtt.dev.icam.school"

# Structure des topics de l'espace privé :
# - Actionneurs (écoute) : bzh/mecatro/prive/<NOM_PROJET>/actionneur/<NOM>
# - Capteurs (envoi)     : bzh/mecatro/prive/<NOM_PROJET>/capteur/<NOM>
TOPIC_SUB_ACTIONNEURS = f"bzh/mecatro/prive/{NOM_PROJET}/actionneur/#"
TOPIC_PUB_CAPTEUR_PRESENCE = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/presence"
TOPIC_PUB_CAPTEUR_POIDS = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/poids"

# Intervalle de remontée des capteurs privés (ex: toutes les 3 secondes)
INTERVALLE_CAPTEURS_MS = 3000

# ==========================================
# MATÉRIEL EMBARQUÉ (Exemple : LED interne de la Pico W)
# ==========================================
try:
    led = Pin("LED", Pin.OUT)  # LED intégrée sur Raspberry Pi Pico W
except:
    led = None

# ==========================================
# 1. FONCTION CALLBACK : RÉCEPTION DES ORDRES (Actionneurs)
# ==========================================
def sur_reception_ordre(topic, msg):
    """
    Fonction appelée automatiquement par check_msg() à chaque réception d'un ordre MQTT.
    """
    topic_str = topic.decode("utf-8")
    msg_str = msg.decode("utf-8").strip()
    
    print(f"\n[ORDRE REÇU] Topic: {topic_str} | Message: {msg_str}")
    
    # 1. Exemple de pilotage d'un moteur ou d'une LED
    if topic_str.endswith("/moteur") or topic_str.endswith("/led"):
        if msg_str.upper() == "ON" or msg_str == "1":
            print("-> Action : Activation du moteur / LED")
            if led:
                led.value(1)
        elif msg_str.upper() == "OFF" or msg_str == "0":
            print("-> Action : Arrêt du moteur / LED")
            if led:
                led.value(0)
                
    # 2. Exemple de déclenchement d'un son / buzzer
    elif topic_str.endswith("/son") or topic_str.endswith("/buzzer"):
        if msg_str.upper() == "PLAY":
            print("-> Action : Sonnerie du buzzer (Bip bip !)")

# ==========================================
# 2. CONNEXION WI-FI & MQTT
# ==========================================
print("Connexion au réseau Wi-Fi...")
ip = connect_to_wifi()
print(f"Wi-Fi connecté ! Adresse IP : {ip}")

print(f"Connexion au Broker : {BROKER_SERVER}...")
clientMQTT = MQTTClientSimple(client_id=CLIENT_ID, server=BROKER_SERVER, ssl=True)

# Définition du callback AVANT la connexion
clientMQTT.set_callback(sur_reception_ordre)

try:
    clientMQTT.connect()
    print("Connecté avec succès au broker MQTT.")
    
    # Abonnement à tous les topics actionneurs du groupe
    clientMQTT.subscribe(topic=TOPIC_SUB_ACTIONNEURS)
    print(f"Abonné aux ordres sur : {TOPIC_SUB_ACTIONNEURS}")
except Exception as e:
    print("Erreur de connexion initiale au broker MQTT :", e)

# ==========================================
# 3. BOUCLE PRINCIPALE NON-BLOQUANTE
# ==========================================
dernier_envoi_capteurs_ms = time.ticks_ms()
presence_simulee = 0

print("\nPrêt à recevoir des ordres et à transmettre les données capteurs...")

while True:
    try:
        # A. Vérification non-bloquante des messages MQTT entrants (déclenche le callback si message reçu)
        clientMQTT.check_msg()
        
        # B. Envoi périodique de l'état des capteurs vers l'application de contrôle
        temps_courant_ms = time.ticks_ms()
        if time.ticks_diff(temps_courant_ms, dernier_envoi_capteurs_ms) >= INTERVALLE_CAPTEURS_MS:
            dernier_envoi_capteurs_ms = temps_courant_ms
            
            # Simulation d'un capteur de présence (0 ou 1) et d'une jauge de poids (en grammes)
            presence_simulee = 1 if presence_simulee == 0 else 0
            poids_mesure = 120 if presence_simulee == 1 else 0
            
            # Envoi simple sur l'espace privé (valeur brute string ou nombre)
            clientMQTT.publish(topic=TOPIC_PUB_CAPTEUR_PRESENCE, msg=str(presence_simulee))
            clientMQTT.publish(topic=TOPIC_PUB_CAPTEUR_POIDS, msg=str(poids_mesure))
            
            print(f"[CAPTEUR PRIVÉ] Présence : {presence_simulee} | Poids : {poids_mesure}g")

    except Exception as e:
        print(f"Erreur détectée dans la boucle : {e}")
        print("Tentative de reconnexion...")
        try:
            connect_to_wifi()
            clientMQTT.connect()
            clientMQTT.subscribe(topic=TOPIC_SUB_ACTIONNEURS)
            print("Reconnexion réussie !")
        except Exception as recon_err:
            print(f"Échec de la reconnexion automatique : {recon_err}")
            
    # Pause courte pour soulager le microcontrôleur
    time.sleep_ms(20)
