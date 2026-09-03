# exemple_telecommande_privee.py
# Exemple de télécommande / contrôle privé pour Raspberry Pi Pico W & Maker Pi Pico
# - Écoute des ordres actionneurs via Callback MQTT (Application -> Pico)
# - Publication des capteurs réels : Boutons BP20, BP21, BP22 et Capteur de température interne

import time
import json
from machine import *
from fasapico import *

# ==========================================
# CONFIGURATION DU PROJET & MQTT
# ==========================================
NOM_PROJET = "miamconnect"

# Structure des topics de l'espace privé :
# - Actionneurs (écoute) : bzh/mecatro/prive/<NOM_PROJET>/actionneur/<NOM>
# - Capteurs (envoi)     : bzh/mecatro/prive/<NOM_PROJET>/capteur/<NOM>
TOPIC_SUB_ACTIONNEURS = f"bzh/mecatro/prive/{NOM_PROJET}/actionneur/#"

TOPIC_PUB_TEMPERATURE = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/temperature"
TOPIC_PUB_BP20 = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/bp20"
TOPIC_PUB_BP21 = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/bp21"
TOPIC_PUB_BP22 = f"bzh/mecatro/prive/{NOM_PROJET}/capteur/bp22"

# Intervalle de remontée périodique des capteurs (ex: toutes les 2 secondes)
INTERVALLE_CAPTEURS_MS = 2000

# ==========================================
# MATÉRIEL EMBARQUÉ (Maker Pi Pico)
# ==========================================
# 1. Actionneurs : LED intégrée et Buzzer (GP18 sur Maker Pi Pico)
try:
    led = Pin("LED", Pin.OUT)
except:
    led = None

try:
    buzzer = Pin(18, Pin.OUT)
except:
    buzzer = None

# 2. Boutons-poussoirs du Maker Pi Pico (connectés à GND lors de l'appui)
bp20 = Pin(20, Pin.IN, Pin.PULL_UP)
bp21 = Pin(21, Pin.IN, Pin.PULL_UP)
bp22 = Pin(22, Pin.IN, Pin.PULL_UP)

# 3. Capteur de température interne de la Pico (ADC 4)
capteur_temp = ADC(4)
CONVERSION_VOLT = 3.3 / 65535

def lire_temperature():
    """Lit la température interne du microcontrôleur RP2040 / RP2350 en °C."""
    tension = capteur_temp.read_u16() * CONVERSION_VOLT
    temperature = 27 - (tension - 0.706) / 0.001721
    return round(temperature, 1)

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
            print("-> Action : Activation de la LED")
            if led:
                led.value(1)
        elif msg_str.upper() == "OFF" or msg_str == "0":
            print("-> Action : Arrêt de la LED")
            if led:
                led.value(0)
                
    # 2. Exemple de déclenchement du buzzer
    elif topic_str.endswith("/son") or topic_str.endswith("/buzzer"):
        if msg_str.upper() == "PLAY" or msg_str == "1":
            print("-> Action : Bip du buzzer")
            if buzzer:
                buzzer.value(1)
                time.sleep_ms(150)
                buzzer.value(0)

# ==========================================
# 2. CLIENT MQTT & ABONNEMENT
# ==========================================
# ClientMQTT gère automatiquement le Wi-Fi, l'heure NTP et la connexion MQTT
clientMQTT = ClientMQTT(callback=sur_reception_ordre)
clientMQTT.subscribe(topic=TOPIC_SUB_ACTIONNEURS)
print(f"Abonné aux ordres sur : {TOPIC_SUB_ACTIONNEURS}")

# ==========================================
# 3. BOUCLE PRINCIPALE NON-BLOQUANTE
# ==========================================
dernier_envoi_capteurs_ms = time.ticks_ms()

print("\nPrêt à recevoir des ordres et à transmettre les données capteurs...")

while True:
    try:
        # A. Vérification non-bloquante des messages MQTT entrants (déclenche le callback si message reçu)
        clientMQTT.check_msg()
        
        # B. Envoi périodique de l'état des capteurs vers l'application de contrôle
        temps_courant_ms = time.ticks_ms()
        if time.ticks_diff(temps_courant_ms, dernier_envoi_capteurs_ms) >= INTERVALLE_CAPTEURS_MS:
            dernier_envoi_capteurs_ms = temps_courant_ms
            
            # Lecture des 3 boutons du Maker Pi Pico (1 si appuyé, 0 si relâché)
            etat_bp20 = 1 if bp20.value() == 0 else 0
            etat_bp21 = 1 if bp21.value() == 0 else 0
            etat_bp22 = 1 if bp22.value() == 0 else 0
            
            # Lecture du capteur de température interne
            temp_mesuree = lire_temperature()
            
            # Envoi simple sur l'espace privé (valeur brute)
            clientMQTT.publish(topic=TOPIC_PUB_TEMPERATURE, msg=str(temp_mesuree))
            clientMQTT.publish(topic=TOPIC_PUB_BP20, msg=str(etat_bp20))
            clientMQTT.publish(topic=TOPIC_PUB_BP21, msg=str(etat_bp21))
            clientMQTT.publish(topic=TOPIC_PUB_BP22, msg=str(etat_bp22))
            
            print(f"[CAPTEURS] Temp: {temp_mesuree}°C | BP20: {etat_bp20} | BP21: {etat_bp21} | BP22: {etat_bp22}")

    except Exception as e:
        print(f"Erreur détectée dans la boucle : {e}")
            
    # Pause courte pour soulager le microcontrôleur
    time.sleep_ms(20)

