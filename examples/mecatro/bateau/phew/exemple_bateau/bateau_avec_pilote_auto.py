# --- Imports ---
from phew import server, access_point, logging, dns
import time
import random
import math
from machine import *

# --- Reseau en mode Point d'acces ---
ap = access_point("Bateau_Pico", "motdepasse")
ip = ap.ifconfig()[0]

# --- Variables globales ---
pilote_auto = False
position_gps_actuelle = (47.645, -2.757)  # Coordonnees initiales fictives
cap_actuel = 0

# --- Broches pour le moteur et le safran ---
PIN_SAFRAN = 15
PIN_ENA = 16
PIN_IN1 = 17
PIN_IN2 = 18

# --- PWM Safran ---
safran_pwm = PWM(Pin(PIN_SAFRAN) , freq = 50)

# --- PWM Moteur ---
ena_pwm = PWM(Pin(PIN_ENA) , freq = 1000)
in1 = Pin(PIN_IN1, Pin.OUT)
in2 = Pin(PIN_IN2, Pin.OUT)


def set_safran(angle):
    angle = max(-90, min(90, angle))
    min_ns = 500_000     # 0.5 ms
    max_ns = 2500_000    # 2.5 ms
    pulse_width = min_ns + int((angle + 90) / 180 * (max_ns - min_ns))
    safran_pwm.duty_ns(pulse_width)
    logging.info(f"[ACTION] Safran regle a {angle}° avec MLI {pulse_width}")

def set_moteur(vitesse):
    vitesse = max(-100, min(100, vitesse))
    sens = 1 if vitesse >= 0 else -1
    duty = int(abs(vitesse) * 65535 / 100)
    print(duty)
    ena_pwm.duty_u16(duty)
    in1.value(1 if sens == 1 else 0)
    in2.value(0 if sens == 1 else 1)
    logging.info(f"[ACTION] Moteur regle a {vitesse}% avec rapport cyclique sur {duty}")

# --- Lecture des capteurs simulee ---
def lire_gps(timer):
    global position_gps_actuelle
    lat, lon = position_gps_actuelle
    delta_lat = -0.00005 + random.uniform(-0.000015, 0.000015)
    delta_lon =  0.00003 + random.uniform(-0.000015, 0.000015)
    position_gps_actuelle = (lat + delta_lat, lon + delta_lon)
    #logging.debug(f"[GPS] Position simulee : {position_gps_actuelle}")

def lire_cap(timer):
    global cap_actuel
    bruit = random.uniform(-8, 8)
    cap_actuel = int((0 + bruit) % 360)
    #logging.debug(f"[CAP] Cap simule : {cap_actuel}°")

def calculer_angle_vers_objectif(lat_actuelle, lon_actuelle, lat_destination, lon_destination):
    # Haversine simplifie + calcul angle cap -> destination
    
    d_lon = math.radians(lon_destination - lon_actuelle)
    y = math.sin(d_lon) * math.cos(math.radians(lat_destination))
    x = math.cos(math.radians(lat_actuelle)) * math.sin(math.radians(lat_destination)) - \
        math.sin(math.radians(lat_actuelle)) * math.cos(math.radians(lat_destination)) * math.cos(d_lon)
    angle = math.degrees(math.atan2(y, x))
    angle = (angle + 360) % 360
    return angle


# --- Pilote automatique ---
def execute_pilote_auto(timer):
    global pilote_auto, position_gps_actuelle
    
    #si le pilote auto est desactive, pas besoin d'aller plus loin
    if not pilote_auto:
        return
    dest_lat, dest_lon = 47.64566, -2.75711  # Coordonnees de l'Icam Vannes
    lat, lon = position_gps_actuelle
    delta_lat = dest_lat - lat
    delta_lon = dest_lon - lon
    if abs(delta_lat) < 0.0001 and abs(delta_lon) < 0.0001:
        set_moteur(0)
        logging.info("[AUTO] Arrive a destination")
        return
    erreur = (angle - cap_actuel + 540) % 360 - 180  # Donne un delta entre -180 et +180
    erreur = max(-90, min(90, erreur))  # Limite pour le servo
    set_safran(erreur)
    set_moteur(80)
    logging.info("[AUTO] Cap sur l'Icam de Vannes")

# --- Routes serveur ---
@server.route("/safran", methods=["GET"])
def regler_safran(request):
    
    #desactivation pilote auto
    global pilote_auto
    pilote_auto = False
    
    angle = int(request.query.get("angle", 0))
    set_safran(angle)
    
    return f"safran regle a {angle}"

@server.route("/vitesse", methods=["GET"])
def modifier_vitesse(request):
    
    #desactivation pilote auto
    global pilote_auto
    pilote_auto = False
    
    vitesse = int(request.query.get("v", 0))
    set_moteur(vitesse)
    
    return f"Vitesse reglee a {vitesse}%"

@server.route("/autopilote", methods=["GET"])
def activer_pilote_auto(request):
    global pilote_auto
    etat = request.query.get("etat", "off")
    pilote_auto = (etat == "on")
    return f"Pilote automatique {'active' if pilote_auto else 'desactive'}"

@server.route("/gps", methods=["GET"])
def afficher_gps(request):
    global position_gps_actuelle
    return f"{position_gps_actuelle}"

@server.route("/cap", methods=["GET"])
def afficher_cap(request):
    global cap_actuel
    return f"{cap_actuel}"

@server.route("/etat")
def get_etat(request):
    return f"cap: {cap_actuel} , GPS: {position_gps_actuelle}, pilote auto: {pilote_auto}"


@server.catchall()
def erreur_404(request):
    return "Page non trouvee", 404

# --- Timers pour interruptions temporelles ---
timer_cap = Timer()
timer_gps = Timer()
timer_auto = Timer()

timer_cap.init(mode=Timer.PERIODIC, period=1000, callback=lire_cap)
timer_gps.init(mode=Timer.PERIODIC, period=3000, callback=lire_gps)
timer_auto.init(mode=Timer.PERIODIC, period=500, callback=execute_pilote_auto)

# --- Lancement du serveur (bloquant) ---
print(f"Serveur demarre en point d'acces WiFi sur [{ip}]")
server.run()
