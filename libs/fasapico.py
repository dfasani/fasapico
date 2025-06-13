import network, time, urequests, json
from machine import *

# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max]
def scale(x, in_min, in_max, out_min, out_max):
    """ Maps two ranges together """
    return (x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min

# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max], return an integer
def scale_to_int(x, in_min, in_max, out_min, out_max):
    return int(scale(x, in_min, in_max, out_min, out_max))


def is_connected_to_wifi():
  wlan = network.WLAN(network.STA_IF)
  return wlan.isconnected()

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30, debug=False):
    statuses = {
        network.STAT_IDLE: "idle",
        network.STAT_CONNECTING: "connecting",
        network.STAT_WRONG_PASSWORD: "wrong password",
        network.STAT_NO_AP_FOUND: "access point not found",
        network.STAT_CONNECT_FAIL: "connection failed",
        network.STAT_GOT_IP: "got ip address"
    }


    wlan = network.WLAN(network.STA_IF)
    
    # 🔄 Réinitialisation propre
    wlan.active(False)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)
    
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    status = wlan.status()

    if debug:
        print(f"Tentative de connexion à {ssid}...")
    
    while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
        status = wlan.status()
        if debug:
            print(f"Statut WiFi mis à jour : {statuses.get(status, 'inconnu')}")
        time.sleep(1)

    if wlan.status() != network.STAT_GOT_IP:
        if debug:
            print(f"Échec de la connexion à {ssid} : {statuses.get(wlan.status(), wlan.status())}")
        raise RuntimeError(f"Network connection to {ssid} failed")

    ifconfig_data = wlan.ifconfig()
    if debug:
        print(f"Configuration réseau complète : {ifconfig_data}")
        print("Attente pour stabilisation du WiFi...")
    
    time.sleep(1)
    return ifconfig_data[0]

# helper method to put the pico into access point mode
def access_point(ssid, password = None):

  # start up network in access point mode  
  wlan = network.WLAN(network.AP_IF)
  wlan.config(essid=ssid)
  if password:
    wlan.config(password=password)
  else:    
    wlan.config(security=0) # disable password
  wlan.active(True)

  return wlan

def get_url(url, debug=False):
    url = url.strip()
    
    if debug:
        print("Je recupere la ressource :", url)
    
    reponse = urequests.get(url)
    contenuDeLaReponse = reponse.content
    reponse.close()
    
    if debug:
        print("Réponse reçue :", contenuDeLaReponse)
    
    return contenuDeLaReponse

def get_json_from_url(url, debug=False):
    contenuDeLaReponse = get_url(url, debug)
    
    if debug:
        print("Je transforme cette chaine en objet JSON :", contenuDeLaReponse)
    
    jsonData = json.loads(contenuDeLaReponse)
    return jsonData


class Moteur:
    def __init__(self, broche_in1, broche_in2, broche_pwm, vitesse=0):
        """
        Initialise le moteur avec les broches spécifiées et une vitesse initiale a 0 par defaut.
        """
        if not all(isinstance(b, int) and 0 <= b <= 27 for b in [broche_in1, broche_in2, broche_pwm]):
            raise ValueError("Les broches doivent être des entiers valides pour la plateforme.")
        
        self.in1 = Pin(broche_in1, Pin.OUT)
        self.in2 = Pin(broche_in2, Pin.OUT)
        self.pwm = PWM(Pin(broche_pwm), freq=1000, duty_u16=0)
        self.etat = "arrêté"  # "avant", "arrière", ou "arrêté"
        self.definir_vitesse(vitesse)

    def definir_vitesse(self, gaz):
        """
        Définit la vitesse (0 à 65535).
        Si la vitesse est un float, elle est convertie en int.
        Lève une exception si la valeur est hors limites.
        """
        if isinstance(gaz, float):
            gaz = int(gaz)
        if not (0 <= gaz <= 65535):
            raise ValueError("La vitesse doit être un entier entre 0 et 65535.")
        self.pwm.duty_u16(gaz)

    def definir_vitesse_pourcentage(self, pourcentage):
        """
        Définit la vitesse en pourcentage (0 à 100).
        """
        if not (0 <= pourcentage <= 100):
            raise ValueError("Le pourcentage doit être entre 0 et 100.")
        gaz = scale_to_int(pourcentage, 0, 100, 0, 65535)
        self.definir_vitesse(gaz)

    def avant(self):
        """Active la rotation en avant."""
        self.in1.low()
        self.in2.high()
        self.etat = "avant"

    def arriere(self):
        """Active la rotation en arrière."""
        self.in1.high()
        self.in2.low()
        self.etat = "arriere"

    def stop(self):
        """Arrête le moteur."""
        self.in1.low()
        self.in2.low()
        self.etat = "stop"

    def set_direction_et_vitesse(self, direction, vitesse):
        """
        Définit la direction ('avant' ou 'arriere') et la vitesse.
        """
        if direction == "avant":
            self.avant()
        elif direction == "arriere":
            self.arriere()
        else:
            raise ValueError("La direction doit être 'avant' ou 'arrière'.")
        self.definir_vitesse(vitesse)

    def arret_progressif(self, pas=500):
        """
        Réduit progressivement la vitesse jusqu'à 0 avant d'arrêter le moteur.
        """
        vitesse_actuelle = self.pwm.duty_u16()
        for v in range(vitesse_actuelle, -1, -pas):
            self.definir_vitesse(max(0, v))
            time.sleep(0.05)  # Pause pour donner le temps au moteur de ralentir
        self.definir_vitesse(0)
        self.stop()

    def get_etat(self):
        """
        Retourne l'état actuel du moteur.
        """
        return {
            "direction": self.etat,
            "vitesse": self.pwm.duty_u16()
        }
    
    def __str__(self):
        # Retourne une chaîne de caractères contenant l'état du moteur
        return f"Moteur({self.in1}, {self.in2}, {self.pwm}, Etat: {self.etat}, PWM: {self.pwm.duty_u16()})"
