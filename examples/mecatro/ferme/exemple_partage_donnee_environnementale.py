# main.py
# Exemple MQTT v2 avec double Callback (MQTT + Timer temporel de 5s) pour Pico W

import time
import json
from machine import Timer  # Importation du module de gestion des Timers
from fasapico import *

# ==========================================
# CONFIGURATION
# ==========================================
CLIENT_ID = "JeanLouisSerreTech"
BROKER_SERVER = "mqtt.dev.icam.school"

# Topics
TOPIC_PUB = "bzh/mecatro/env/pression_atmospherique"

# Variable globale (Drapeau / Flag) pour le Timer
publier_maintenant = False

# ==========================================
# 1. CALLBACK DU TIMER (Déclenché toutes les 5s)
# ==========================================
def declencher_publication(t):
    """
    Cette fonction est appelée automatiquement par le Timer toutes les 5 secondes.
    Elle doit être extrêmement rapide, donc on ne fait que lever un drapeau.
    Le paramètre 't' est obligatoire (il reçoit l'objet Timer lui-même).
    """
    global publier_maintenant
    publier_maintenant = True

# ==========================================
# 2. CALLBACK MQTT (Réception de messages)
# ==========================================
def sur_reception_message(topic, msg):
    """
    Appelé automatiquement dès qu'un message arrive sur TOPIC_SUB.
    """
    topic_recu = topic.decode('utf-8')
    message_recu = msg.decode('utf-8')
    
    print(f"\n[CALLBACK MQTT] Message reçu sur {topic_recu} !")
    print(f"[CALLBACK MQTT] Contenu : {message_recu}")
    
    try:
        commande = json.loads(message_recu)
        if "led" in commande:
            if commande["led"] == "ON":
                print("-> Action : Allumer la LED de la Pico")
            elif commande["led"] == "OFF":
                print("-> Action : Éteindre la LED de la Pico")
    except ValueError:
        print(f"[CALLBACK MQTT] Message brut : {message_recu}")

# ==========================================
# CONNEXION WI-FI ET CONFIGURATION MQTT
# ==========================================
print("Connexion au réseau Wi-Fi...")
ip = connect_to_wifi()
print(f"Wi-Fi connecté ! IP : {ip}")

print(f"Connexion au Broker : {BROKER_SERVER}...")
clientMQTT = MQTTClientSimple(client_id=CLIENT_ID, server=BROKER_SERVER, ssl=True)

# Liaison du callback MQTT (avant connexion)
clientMQTT.set_callback(sur_reception_message)

try:
    clientMQTT.connect()
    print("Connecté au broker MQTT.")
    clientMQTT.subscribe(topic=TOPIC_SUB)
    print(f"Abonné au topic : {TOPIC_SUB}")
except Exception as e:
    print("Erreur d'initialisation MQTT :", e)

# ==========================================
# 3. INITIALISATION DU TIMER TEMPOREL (5 sec)
# ==========================================
# On crée un timer virtuel (-1)
mon_timer = Timer(-1)

# Configuration : 5000 ms (5 secondes), répétitif (PERIODIC)
mon_timer.init(
    period=5000, 
    mode=Timer.PERIODIC, 
    callback=declencher_publication
)
print("Timer temporel démarré (cadence : 5000ms / 0.2 Hz).")

# ==========================================
# BOUCLE PRINCIPALE (Ultra-légère et réactive)
# ==========================================
print("En attente de messages et prêt à publier...")

while True:
    try:
        # Écoute en continu du broker MQTT (s'exécute quasi instantanément)
        clientMQTT.check_msg()
        
        # Si le Timer a levé le drapeau (toutes les 5s)
        if publier_maintenant:
            # 1. On baisse immédiatement le drapeau
            publier_maintenant = False
            
            # 2. On prépare nos données JSON
            valeur_pression = 1025  # Simulation capteur
            donnees_capteur = {
                "valeur": valeur_pression,
                "unite": "hPa",
                "type": "pression atmosphérique"
            }
            payload_json = json.dumps(donnees_capteur)
            
            # 3. On publie sur le réseau
            clientMQTT.publish(topic=TOPIC_PUB, msg=payload_json, retain=True)
            print(f"[TIMER EVENT] Publication effectuée : {payload_json}")
            
    except Exception as e:
        print(f"Erreur détectée : {e}")
        print("Tentative de reconnexion...")
        try:
            connect_to_wifi()
            clientMQTT.connect()
            clientMQTT.subscribe(topic=TOPIC_SUB)
        except Exception as recon_err:
            print("Échec de la reconnexion :", recon_err)
            
    # Très courte pause de sécurité pour soulager le processeur
    time.sleep(0.05)