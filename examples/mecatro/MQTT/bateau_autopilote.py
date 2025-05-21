# --- Imports ---
from mqtt import MQTTClientSimple
from fasapico import *
from machine import *
import time
import random
import math

# --- Connexion WiFi ---
print("Connexion au réseau WiFi...")
ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")
print("\nConnecté ! Adresse IP :", ip)

# --- Variables globales ---
pilote_auto = False
position_gps_actuelle = (47.645, -2.757)
cap_actuel = 0

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
    print(f"[ACTION] Safran réglé à {angle}°")

def set_moteur(vitesse):
    vitesse = max(-100, min(100, vitesse))
    sens = 1 if vitesse >= 0 else -1
    duty = int(abs(vitesse) * 65535 / 100)
    ena_pwm.duty_u16(duty)
    in1.value(1 if sens == 1 else 0)
    in2.value(0 if sens == 1 else 1)
    print(f"[ACTION] Moteur réglé à {vitesse}%")

# --- Capteurs simulés ---
def lire_gps(timer):
    global position_gps_actuelle
    lat, lon = position_gps_actuelle
    delta_lat = -0.00005 + random.uniform(-0.000015, 0.000015)
    delta_lon = 0.00003 + random.uniform(-0.000015, 0.000015)
    position_gps_actuelle = (lat + delta_lat, lon + delta_lon)
    clientMQTT.publish("bateau/gps", f"{position_gps_actuelle[0]:.5f},{position_gps_actuelle[1]:.5f}")

def lire_cap(timer):
    global cap_actuel
    bruit = random.uniform(-8, 8)
    cap_actuel = int((0 + bruit) % 360)
    clientMQTT.publish("bateau/cap", str(cap_actuel))

# --- Pilote automatique ---
def execute_pilote_auto(timer):
    global pilote_auto, position_gps_actuelle, cap_actuel
    if not pilote_auto:
        return
    dest_lat, dest_lon = 47.64566, -2.75711 # coordonnées Icam Bretagne
    lat, lon = position_gps_actuelle
    if abs(dest_lat - lat) < 0.0001 and abs(dest_lon - lon) < 0.0001:
        set_moteur(0)
        print("[AUTO] Arrivé à destination")
        return
    angle = calculer_angle_vers_objectif(lat, lon, dest_lat, dest_lon)
    erreur = (angle - cap_actuel + 540) % 360 - 180
    erreur = max(-90, min(90, erreur))
    set_safran(erreur)
    set_moteur(80)
    print("[AUTO] Cap sur l'Icam")

def calculer_angle_vers_objectif(lat1, lon1, lat2, lon2):
    d_lon = math.radians(lon2 - lon1)
    y = math.sin(d_lon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(d_lon)
    angle = math.degrees(math.atan2(y, x))
    return (angle + 360) % 360

# --- MQTT : réception des commandes ---
def on_message_callback(topic, msg):
    global pilote_auto
    topic = topic.decode()
    msg = msg.decode()
    print("MQTT reçu >>", topic, msg)

    if topic == "bateau/safran":
        try:
            pilote_auto = False
            angle = int(msg)
            set_safran(angle)
        except ValueError:
            print("Valeur safran invalide")
    elif topic == "bateau/vitesse":
        try:
            pilote_auto = False
            vitesse = int(msg)
            set_moteur(vitesse)
        except ValueError:
            print("Valeur vitesse invalide")
    elif topic == "bateau/autopilote":
        pilote_auto = msg.lower() == "on"

# --- Connexion MQTT ---
print("Connexion au broker MQTT")
clientMQTT = MQTTClientSimple(client_id="DavidFasani7685", server="broker.emqx.io")
clientMQTT.set_callback(on_message_callback)
clientMQTT.connect()
clientMQTT.subscribe("bateau/safran")
clientMQTT.subscribe("bateau/vitesse")
clientMQTT.subscribe("bateau/autopilote")
print("Abonnements OK")

# --- Timers capteurs et autopilote ---
Timer(mode=Timer.PERIODIC, period=1000, callback=lire_cap)
Timer(mode=Timer.PERIODIC, period=3000, callback=lire_gps)
Timer(mode=Timer.PERIODIC, period=500, callback=execute_pilote_auto)

print("🚤 Bateau prêt. MQTT actif.")

while True:
    clientMQTT.wait_msg()
