import network, time, urequests, json

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
def connect_to_wifi(ssid, password, timeout_seconds=30):
  statuses = {
    network.STAT_IDLE: "idle",
    network.STAT_CONNECTING: "connecting",
    network.STAT_WRONG_PASSWORD: "wrong password",
    network.STAT_NO_AP_FOUND: "access point not found",
    network.STAT_CONNECT_FAIL: "connection failed",
    network.STAT_GOT_IP: "got ip address"
  }

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)    
  wlan.connect(ssid, password)
  start = time.ticks_ms()
  status = wlan.status()

  
  while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
    new_status = wlan.status()
    if status != new_status:
      status = new_status
    time.sleep(0.25)

  if wlan.status() != 3:
    raise RuntimeError('network connection to ' + str(ssid) + ' failed')

  return wlan.ifconfig()[0]

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

def get_url(url):
   
    #retirer le commentaire pour debuger
    print("Je recupere la ressource :",url)
    
    reponse = urequests.get(url)
    contenuDeLaReponse = reponse.content #recupere le corps de la reponse
    reponse.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
    
    #retirer le commentaire pour debuger
    #print(corps)
    return contenuDeLaReponse

def get_json_from_url(url):
    #recuperation du document
    contenuDeLaReponse = get_url(url)




class Moteur:
    def __init__(self, broche_in1, broche_in2, broche_pwm , vitesse=0):
        self.in1 = Pin(broche_in1, Pin.OUT)
        self.in2 = Pin(broche_in2, Pin.OUT)
        self.pwm = PWM(broche_pwm , freq=1000 , duty_u16=0)
        self.definir_vitesse(vitesse)
        

    def definir_vitesse(self, gaz):
        """
        Définit la vitesse (0 à 65535).
        Si la vitesse est un float, elle est convertie en int.
        Lève une exception si la valeur est hors limites.
        """
        if isinstance(gaz, float):
            vitesse = int(gaz)
        if not (0 <= gaz <= 65535):
            raise ValueError("La vitesse doit être un entier entre 0 et 65535.")
        self.pwm.duty_u16(gaz)

    def avant(self):
        """Active la rotation en avant."""
        self.in1.low()
        self.in2.high()

    def arriere(self):
        """Active la rotation en arrière."""
        self.in1.high()
        self.in2.low()

    def stop(self):
        """Arrête le moteur."""
        self.in1.low()
        self.in2.low()

    print("Je transforme cette chaine en objet JSON :" , contenuDeLaReponse)
    
    jsonData = json.loads(contenuDeLaReponse)
    return jsonData
