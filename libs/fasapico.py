# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max]
def scale(x, in_min, in_max, out_min, out_max):
    """ Maps two ranges together """
    return (x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min

# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max], return an integer
def scale_to_int(x, in_min, in_max, out_min, out_max):
    return int(scale(x, in_min, in_max, out_min, out_max))


def is_connected_to_wifi():
  import network, time
  wlan = network.WLAN(network.STA_IF)
  return wlan.isconnected()

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  import network, time

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
    return None

  return wlan.ifconfig()[0]

# helper method to put the pico into access point mode
def access_point(ssid, password = None):
  import network

  # start up network in access point mode  
  wlan = network.WLAN(network.AP_IF)
  wlan.config(essid=ssid)
  if password:
    wlan.config(password=password)
  else:    
    wlan.config(security=0) # disable password
  wlan.active(True)

  return wlan



def get_json_from_url(url):
    import urequests, json
    
    #retirer le commentaire pour debuger
    #print("Sending request to :",url)
    
    reponse = urequests.get(url)
    contenuDeLaReponse = reponse.content #recupere le corps de la reponse
    reponse.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
    
    #retirer le commentaire pour debuger
    #print(corps)
    
    jsonData = json.loads(contenuDeLaReponse)
    return jsonData
