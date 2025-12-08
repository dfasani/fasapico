# --- Imports ---
from fasapico import *
from machine import *
import network
import time
import random
import math
import logging
import sys
import secrets

logging.enable_logging_types(logging.LOG_DEBUG)



# --- Variables globales ---
pilote_auto = False
position_gps_actuelle = (47.645, -2.757)
cap_actuel = 0
clientMQTT = None

# --- Broches pour le moteur et le safran ---
PIN_SAFRAN = 15
PIN_ENA = 16
PIN_IN1 = 17
PIN_IN2 = 18

# --- PWM Safran ---
safran_pwm = PWM(Pin(PIN_SAFRAN), freq=50)

# --- PWM Moteur ---
ena_pwm = PWM(Pin(PIN_ENA), freq=1000)
in1 = Pin(PIN_IN1, Pin.OUT)
in2 = Pin(PIN_IN2, Pin.OUT)

# --- Fonctions actionneurs ---
def set_safran(angle):
    angle = max(-90, min(90, angle))
    min_ns = 500_000
    max_ns = 2500_000
    pulse_width = min_ns + int((angle + 90) / 180 * (max_ns - min_ns))
    safran_pwm.duty_ns(pulse_width)
    logging.info(f"Safran réglé à {angle}°")

def set_moteur(vitesse):
    vitesse = max(-100, min(100, vitesse))
    sens = 1 if vitesse >= 0 else -1
    duty = int(abs(vitesse) * 65535 / 100)
    ena_pwm.duty_u16(duty)
    in1.value(1 if sens == 1 else 0)
    in2.value(0 if sens == 1 else 1)
    logging.info(f"Moteur réglé à {vitesse}%")

# --- Capteurs simulés ---
def lire_gps(timer):
    global position_gps_actuelle
    global clientMQTT
    
    if clientMQTT is None :
        return
    
    lat, lon = position_gps_actuelle
    delta_lat = -0.00005 + random.uniform(-0.000015, 0.000015)
    delta_lon = 0.00003 + random.uniform(-0.000015, 0.000015)
    position_gps_actuelle = (lat + delta_lat, lon + delta_lon)
    position_gps_actuelle = (lat + delta_lat, lon + delta_lon)
    try:
        clientMQTT.publish("bzh/iot/bateau/monBateau/gps", f"{position_gps_actuelle[0]:.5f},{position_gps_actuelle[1]:.5f}")
    except Exception as e:
        logging.error(f"Erreur publication GPS MQTT: {e}")

def lire_cap(timer):
    global cap_actuel
    global clientMQTT
    
    if clientMQTT is None :
        return
    
    bruit = random.uniform(-8, 8)
    cap_actuel = int((0 + bruit) % 360)
    try:
        clientMQTT.publish("bzh/iot/bateau/monBateau/cap", str(cap_actuel))
    except Exception as e:
        logging.error(f"Erreur publication cap MQTT: {e}")

# ... (omitted code) ...

# --- MQTT : réception des commandes ---
def on_message_callback(topic, msg):
    global pilote_auto
    try:
        topic = topic.decode()
        msg = msg.decode()
        logging.info(f"MQTT reçu >> {topic} : {msg}")

        if topic == "bzh/iot/bateau/monBateau/safran":
            pilote_auto = False
            angle = int(msg)
            set_safran(angle)
        elif topic == "bzh/iot/bateau/monBateau/vitesse":
            pilote_auto = False
            vitesse = int(msg)
            set_moteur(vitesse)
        elif topic == "bzh/iot/bateau/monBateau/autopilote":
            pilote_auto = msg.lower() == "on"
    except Exception as e:
        logging.error(f"Erreur traitement message MQTT: {e}")


# ... (omitted code) ...

        # test connexion MQTT
        if clientMQTT is not None:
            try:
                clientMQTT.publish("bzh/iot/bateau/monBateau/debug", "still alive")
                logging.info("Accès broker MQTT [OK]")
                return
            except Exception as e:
                logging.warning(f"Erreur vérification connexion MQTT: {e}")

        # connexion MQTT
        logging.info("Connexion au broker MQTT...")
        clientMQTT = MQTTClientSimple(client_id="DavidFasani7685", server="mqtt.dev.icam.school", ssl=True)
        clientMQTT.set_callback(on_message_callback)
        clientMQTT.connect()

        clientMQTT.subscribe("bzh/iot/bateau/monBateau/safran")
        clientMQTT.subscribe("bzh/iot/bateau/monBateau/vitesse")
        clientMQTT.subscribe("bzh/iot/bateau/monBateau/autopilote")
        logging.info("Abonnements MQTT OK")
        
        clientMQTT.publish("bzh/iot/bateau/monBateau/debug" , "reco ok")

    except Exception as e:
        logging.error(f"Exception dans network_check: {e}")
        # on peut aussi logger le traceback si besoin, mais ça peut être verbeux sur microcontrôleur



#TODO : differencier lirecap, liregps et publier les capteurs qui peut etre fait plus souvent

# Timers capteurs et autopilote
Timer(mode=Timer.PERIODIC, period=1000, callback=lire_cap)
Timer(mode=Timer.PERIODIC, period=3000, callback=lire_gps)
Timer(mode=Timer.PERIODIC, period=500, callback=execute_pilote_auto)
Timer(mode=Timer.PERIODIC, period=10000, callback=network_check)

logging.info("Bateau prêt. Démarrage de MQTT...")

# --- Boucle principale ---

while True:
    try:
        clientMQTT.wait_msg()

    except Exception as e:
        logging.error(f"Erreur reseau: {e}")
        time.sleep(5)
        network_check(None)
