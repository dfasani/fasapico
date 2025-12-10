import network
import time
import utime
import urequests
import json
import math
import sys
import usocket as socket
import ustruct as struct
import os
import gc
from ubinascii import hexlify
from machine import I2C, Pin, SoftI2C, PWM, ADC, UART, Timer
import machine

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
def connect_to_wifi(ssid=None, password=None, timeout_seconds=30, debug=False):
    if ssid is None or password is None:
        try:
            import secrets
            ssid = ssid or getattr(secrets, 'ssid', None)
            password = password or getattr(secrets, 'password', None)
            if ssid is None or password is None:
               raise ValueError("secrets.py must contain 'ssid' and 'password'")
        except ImportError:
            print("Erreur: secrets.py introuvable et pas d'arguments fournis.")
            raise ValueError("SSID/Password not provided and secrets.py missing")

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

def decode_bytes(data):
    """
    Décode les bytes en string utf-8 de manière sûre.
    Retourne la donnée brute ou string.
    """
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except:
            return data
    return data

def check_internet_connection(dns_server="8.8.8.8", port=53):
    """
    Vérifie l'accès internet en tentant une connexion DNS simple.
    """
    try:
        addr = socket.getaddrinfo(dns_server, port)[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s.close()
        return True
    except:
        return False

def manage_mqtt_connection(client, server_broker, client_id, topic_cmd, callback, port=1883):
    """
    Gère la connexion WiFi et MQTT.
    Retourne l'objet client MQTT (connecté ou None si échec).
    
    - client: instance MQTTClient actuelle (peut être None)
    - server_broker: adresse du broker
    - client_id: ID du client MQTT
    - topic_cmd: Topic principal pour l'abonnement
    - callback: fonction de rappel pour les messages reçus
    - port: Port MQTT (default 1883)
    """
    # 1. Check WiFi
    if not is_connected_to_wifi():
        warn("WiFi perdu. Tentative de reconnexion auto via secrets...")
        try:
            connect_to_wifi() # Utilise secrets.py
        except Exception as e:
            error(f"Echec reconnexion WiFi: {e}")
            return None

    # 1c. Check Internet (Optionnel mais recommandé)
    if not check_internet_connection():
        error("Pas d'accès internet (Ping fail).")
        return None

    # 2. Check MQTT existant
    if client:
        try:
            client.ping()
            return client # Tout va bien
        except:
            error("Lien MQTT mort.")
            client = None # On force la reconnexion

    # 3. (Re)Connect MQTT
    if client is None:
        try:
            info(f"Connexion au broker {server_broker}:{port}...")
            # Petit délai stabilisateur
            time.sleep(1)
            
            client = MQTTClientSimple(
                client_id=client_id,
                server=server_broker,
                port=port
            )
            client.set_callback(callback)
            client.connect()
            
            if topic_cmd:
                info(f"Abonnement à {topic_cmd}")
                client.subscribe(topic_cmd)
            
            info("MQTT Connecté & Abonné !")
            return client
            
        except Exception as e:
             error(f"Echec Connexion MQTT: {e}")
             return None

    return client


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


# ==========================================
# Voiture Class
# ==========================================

class Voiture:
    def __init__(self, moteur_a, moteur_b, moteur_c, moteur_d):
        """Initialisation de la voiture avec 4 moteurs"""
        self.moteur_a = moteur_a
        self.moteur_b = moteur_b
        self.moteur_c = moteur_c
        self.moteur_d = moteur_d

    def avancer(self):
        self.moteur_a.avant()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.avant()

    def reculer(self):
        self.moteur_a.arriere()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.arriere()

    def glisser_droite(self):
        self.moteur_a.arriere()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.arriere()

    def glisser_gauche(self): 
        self.moteur_a.avant()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.avant()

    def rotation_horaire(self):
        self.moteur_a.avant()
        self.moteur_b.arriere()
        self.moteur_c.avant()
        self.moteur_d.arriere()

    def rotation_anti_horaire(self):
        self.moteur_a.arriere()
        self.moteur_b.avant()
        self.moteur_c.arriere()
        self.moteur_d.avant()

    def diagonale_avant_droite(self):
        self.moteur_a.stop()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.stop()
        
    def diagonale_arriere_gauche(self):
        self.moteur_a.stop()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.stop()

    def diagonale_avant_gauche(self):
        self.moteur_a.avant()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.avant()

    def diagonale_arriere_droite(self):
        self.moteur_a.arriere()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.arriere()


    def stop(self):
        self.moteur_a.stop()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.stop()
        
        self.moteur_d.definir_vitesse(gaz)

    
# ==========================================
# MqttHandler Class
# ==========================================
class MqttHandler:
    def __init__(self, broker, port, client_id, topic_cmd=None, callback=None):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.topic_cmd = topic_cmd
        self.callback = callback
        self.client = None

    def check_connection(self, timer=None):
        """
        Vérifie et rétablit la connexion MQTT si nécessaire.
        Peut être utilisé comme callback de Timer.
        """
        self.client = manage_mqtt_connection(
            client=self.client,
            server_broker=self.broker,
            client_id=self.client_id,
            topic_cmd=self.topic_cmd,
            callback=self.callback,
            port=self.port
        )
        return self.client
    
    def publish(self, topic, message):
        """
        Publie un message si connecté.
        """
        if self.client:
            try:
                self.client.publish(topic, str(message))
            except Exception as e:
                error(f"Erreur publish {topic}: {e}")
        else:
            pass

    def check_msg(self):
        """
        Vérifie les messages entrants (doit être appelé dans la boucle principale).
        """
        if self.client:
             try:
                 self.client.check_msg()
             except Exception as e:
                 error(f"Erreur check_msg: {e}") 


    



# ==========================================
# Stepper Class
# ==========================================

class Stepper:
    def __init__(self, pin1=10, pin2=11, pin3=12, pin4=13):
        self.pins = [Pin(pin1, Pin.OUT), Pin(pin2, Pin.OUT), Pin(pin3, Pin.OUT), Pin(pin4, Pin.OUT)]

    def move(self, nbPas):
        if nbPas > 0:
            steps_sequence = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        else:
            steps_sequence = [[0,0,0,1], [0,0,1,0], [0,1,0,0], [1,0,0,0]]
            
        for _ in range(abs(nbPas)):
            for step in steps_sequence:
                for i in range(4):
                    self.pins[i].value(step[i])
                time.sleep_ms(5)


# ==========================================
# MQTT Classes
# ==========================================

class MQTTException(Exception):
    pass


class MQTTClientSimple:
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params={},
    ):
        # Ensure port is an integer (accept strings like "1883")
        if isinstance(port, str):
            try:
                port = int(port)
            except ValueError:
                raise MQTTException("Invalid port value: must be an integer or numeric string")

        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self.lw_retain = False

    def _to_bytes(self, s):
        # Accept either bytes or str. If str, encode as utf-8.
        if isinstance(s, bytes):
            return s
        if isinstance(s, str):
            return s.encode("utf-8")
        # Fallback: convert to str then encode
        return str(s).encode("utf-8")

    def _send_str(self, s):
        b = self._to_bytes(s)
        # send 2-byte length followed by bytes
        self.sock.write(struct.pack("!H", len(b)))
        self.sock.write(b)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)[0]
            n |= (b & 0x7F) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl

            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")

        # Use byte lengths for utf-8 correctness
        client_id_b = self._to_bytes(self.client_id)
        sz = 10 + 2 + len(client_id_b)
        msg[6] = clean_session << 1
        if self.user is not None:
            user_b = self._to_bytes(self.user)
            pswd_b = self._to_bytes(self.pswd)
            sz += 2 + len(user_b) + 2 + len(pswd_b)
            msg[6] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[7] |= self.keepalive >> 8
            msg[8] |= self.keepalive & 0x00FF
        if self.lw_topic:
            lw_topic_b = self._to_bytes(self.lw_topic)
            lw_msg_b = self._to_bytes(self.lw_msg)
            sz += 2 + len(lw_topic_b) + 2 + len(lw_msg_b)
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz

        self.sock.write(premsg, i + 2)
        self.sock.write(msg)
        # print(hex(len(msg)), hexlify(msg, ":"))
        # send client id as bytes
        self._send_str(client_id_b)
        if self.lw_topic:
            self._send_str(lw_topic_b)
            self._send_str(lw_msg_b)
        if self.user is not None:
            self._send_str(user_b)
            self._send_str(pswd_b)
        resp = self.sock.read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self.sock.write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self.sock.write(b"\xc0\0")
    #David : inversion ordre : qos et retain
    def publish(self, topic, msg , qos=0 , retain=False):
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        # ensure we use byte lengths for topic and msg
        topic_b = self._to_bytes(topic)
        msg_b = self._to_bytes(msg)
        sz = 2 + len(topic_b) + len(msg_b)
        if qos > 0:
            sz += 2
        assert sz < 2097152
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        # print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt, i + 1)
        self._send_str(topic_b)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.write(pkt, 2)
        self.sock.write(msg_b)
        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self.sock.read(1)
                    assert sz == b"\x02"
                    rcv_pid = self.sock.read(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        return
        elif qos == 2:
            assert 0

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        topic_b = self._to_bytes(topic)
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        # length: 2 (packet id) + 2 + len(topic) + 1 (qos)
        total_len = 2 + 2 + len(topic_b) + 1
        struct.pack_into("!BH", pkt, 1, total_len, self.pid)
        # print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt)
        self._send_str(topic_b)
        self.sock.write(qos.to_bytes(1, "little"))
        while 1:
            op = self.wait_msg()
            if op == 0x90:
                resp = self.sock.read(4)
                # print(resp)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                if resp[3] == 0x80:
                    raise MQTTException(resp[3])
                return

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        res = self.sock.read(1)
        self.sock.setblocking(True)
        if res is None:
            return None
        if res == b"":
            raise OSError(-1)
        if res == b"\xd0":  # PINGRESP
            sz = self.sock.read(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xF0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self.sock.read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic_b = self.sock.read(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self.sock.read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self.sock.read(sz)
        # decode topic and message to utf-8 strings before calling callback
        try:
            topic = topic_b.decode("utf-8")
        except Exception:
            topic = topic_b
        try:
            msg_decoded = msg.decode("utf-8")
        except Exception:
            msg_decoded = msg
        # call the callback with decoded (or raw bytes if decode fails)
        self.cb(topic, msg_decoded)
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self.sock.write(pkt)
        elif op & 6 == 4:
            assert 0
        return op

    # Checks whether a pending message from server is available.
    # If not, returns immediately with None. Otherwise, does
    # the same processing as wait_msg.
    def check_msg(self):
        self.sock.setblocking(False)
        return self.wait_msg()


class MQTTClient(MQTTClientSimple):
    DELAY = 2
    DEBUG = False

    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self):
        i = 0
        while 1:
            try:
                return super().connect(False)
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)

    def publish(self, topic, msg, retain=False, qos=0):
        while 1:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def wait_msg(self):
        while 1:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def check_msg(self, attempts=2):
        while attempts:
            self.sock.setblocking(False)
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()
            attempts -= 1


# ==========================================
# bmm150 Class
# ==========================================

class trim_register:
  def __init__(self):
    self.dig_x1   = 0
    self.dig_y1   = 0
    self.dig_x2   = 0
    self.dig_y2   = 0
    self.dig_z1   = 0
    self.dig_z2   = 0
    self.dig_z3   = 0
    self.dig_z4   = 0
    self.dig_xy1  = 0
    self.dig_xy2  = 0
    self.dig_xyz1 = 0
_trim_data = trim_register()

class geomagnetic_data:
  def __init__(self):
    self.x   = 0
    self.y   = 0
    self.z   = 0
    self.r   = 0
_geomagnetic = geomagnetic_data()

class bmm150(object):
  PI                             = 3.141592653
  ENABLE_POWER                   = 1
  DISABLE_POWER                  = 0
  POLARITY_HIGH                  = 1
  POLARITY_LOW                   = 0
  ERROR                          = -1
  SELF_TEST_XYZ_FALL             = 0
  SELF_TEST_YZ_FAIL              = 1
  SELF_TEST_XZ_FAIL              = 2
  SELF_TEST_Z_FAIL               = 3
  SELF_TEST_XY_FAIL              = 4
  SELF_TEST_Y_FAIL               = 5
  SELF_TEST_X_FAIL               = 6
  SELF_TEST_XYZ_OK               = 7
  DRDY_ENABLE                    = 1
  DRDY_DISABLE                   = 0
  INTERRUPUT_LATCH_ENABLE        = 1
  INTERRUPUT_LATCH_DISABLE       = 0
  MEASUREMENT_X_ENABLE           = 0
  MEASUREMENT_Y_ENABLE           = 0
  MEASUREMENT_Z_ENABLE           = 0
  MEASUREMENT_X_DISABLE          = 1
  MEASUREMENT_Y_DISABLE          = 1
  MEASUREMENT_Z_DISABLE          = 1
  DATA_OVERRUN_ENABLE            = 1
  DATA_OVERRUN_DISABLE           = 0
  OVERFLOW_INT_ENABLE            = 1
  OVERFLOW_INT_DISABLE           = 0
  INTERRUPT_X_ENABLE             = 0
  INTERRUPT_Y_ENABLE             = 0
  INTERRUPT_Z_ENABLE             = 0
  INTERRUPT_X_DISABLE            = 1
  INTERRUPT_Y_DISABLE            = 1
  INTERRUPT_Z_DISABLE            = 1
  
  CHANNEL_X                      = 1
  CHANNEL_Y                      = 2
  CHANNEL_Z                      = 3
  ENABLE_INTERRUPT_PIN           = 1
  DISABLE_INTERRUPT_PIN          = 0
  POWERMODE_NORMAL               = 0x00
  POWERMODE_FORCED               = 0x01
  POWERMODE_SLEEP                = 0x03
  POWERMODE_SUSPEND              = 0x04
  PRESETMODE_LOWPOWER            = 0x01
  PRESETMODE_REGULAR             = 0x02
  PRESETMODE_HIGHACCURACY        = 0x03
  PRESETMODE_ENHANCED            = 0x04
  REPXY_LOWPOWER                 = 0x01
  REPXY_REGULAR                  = 0x04
  REPXY_ENHANCED                 = 0x07
  REPXY_HIGHACCURACY             = 0x17
  REPZ_LOWPOWER                  = 0x01
  REPZ_REGULAR                   = 0x07
  REPZ_ENHANCED                  = 0x0D
  REPZ_HIGHACCURACY              = 0x29
  CHIP_ID_VALUE                  = 0x32
  CHIP_ID_REGISTER               = 0x40
  REG_DATA_X_LSB                 = 0x42
  REG_DATA_READY_STATUS          = 0x48
  REG_INTERRUPT_STATUS           = 0x4a
  CTRL_POWER_REGISTER            = 0x4b
  MODE_RATE_REGISTER             = 0x4c
  REG_INT_CONFIG                 = 0x4D
  REG_AXES_ENABLE                = 0x4E
  REG_LOW_THRESHOLD              = 0x4F
  REG_HIGH_THRESHOLD             = 0x50
  REG_REP_XY                     = 0x51
  REG_REP_Z                      = 0x52
  RATE_10HZ                      = 0x00        #(default rate)
  RATE_02HZ                      = 0x01
  RATE_06HZ                      = 0x02
  RATE_08HZ                      = 0x03
  RATE_15HZ                      = 0x04
  RATE_20HZ                      = 0x05
  RATE_25HZ                      = 0x06
  RATE_30HZ                      = 0x07
  DIG_X1                         = 0x5D
  DIG_Y1                         = 0x5E
  DIG_Z4_LSB                     = 0x62
  DIG_Z4_MSB                     = 0x63
  DIG_X2                         = 0x64
  DIG_Y2                         = 0x65
  DIG_Z2_LSB                     = 0x68
  DIG_Z2_MSB                     = 0x69
  DIG_Z1_LSB                     = 0x6A
  DIG_Z1_MSB                     = 0x6B
  DIG_XYZ1_LSB                   = 0x6C
  DIG_XYZ1_MSB                   = 0x6D
  DIG_Z3_LSB                     = 0x6E
  DIG_Z3_MSB                     = 0x6F
  DIG_XY2                        = 0x70
  DIG_XY1                        = 0x71
  LOW_THRESHOLD_INTERRUPT        = 0x00
  HIGH_THRESHOLD_INTERRUPT       = 0x01
  NO_DATA                        = -32768
  __txbuf          = [0]          # i2c send buffer
  __threshold_mode = 2
  def __init__(self , sdaPin , sclPin):
    timeout = utime.time() + 10 # 10 sec
    while True:
        self.i2cbus = SoftI2C(scl=Pin(sclPin), sda=Pin(sdaPin), freq=100000)
        devices = self.i2cbus.scan()

        if 19 in devices: # 0x13 is 19
            print("[INFO] BMM150 found!")
            utime.sleep_ms(100) # Wait for stabilization
            break
        if utime.time() > timeout:
            print("[ERROR] BMM150 init timeout")
            break
        
        utime.sleep_ms(100)

    self.address = 0x13

  def read_reg(self, reg, len):
    for attempt in range(3):
        try:
            return list(self.i2cbus.readfrom_mem(self.address, reg, len))
        except OSError:
            if attempt == 2: raise
            utime.sleep_ms(10)

  def write_reg(self, reg, data):
    if isinstance(data, int):
        buf = bytearray([data])
    elif isinstance(data, list):
        buf = bytearray(data)
    else:
        buf = data
    
    for attempt in range(3):
        try:
            self.i2cbus.writeto_mem(self.address, reg, buf)
            break
        except OSError:
            if attempt == 2: raise
            utime.sleep_ms(10)


  def sensor_init(self):
    '''!
      @brief Init bmm150 check whether the chip id is right
      @return 0  is init success
              -1 is init failed
    '''
    self.set_power_bit(self.ENABLE_POWER)
    chip_id = self.get_chip_id()
    if chip_id == self.CHIP_ID_VALUE:
      self.get_trim_data()
      return 0
    else:
      return -1

  
  def get_chip_id(self):
    '''!
      @brief get bmm150 chip id
      @return chip id
    '''
    rslt = self.read_reg(self.CHIP_ID_REGISTER, 1)
    return rslt[0]

  def soft_reset(self):
    '''!
      @brief Soft reset, restore to suspend mode after soft reset and then enter sleep mode, soft reset can't be implemented under suspend mode
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    self.__txbuf[0] = rslt[0] | 0x82
    self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)

  def self_test(self):
    '''!
      @brief Sensor self test, the returned character string indicate the self test result.
      @return The character string of the test result
    '''
    str1 = ""
    self.set_operation_mode(self.POWERMODE_SLEEP)
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    self.__txbuf[0] == rslt[0] | 0x01
    self.write_reg(self.MODE_RATE_REGISTER, self.__txbuf)
    utime.sleep(1)
    rslt = self.read_reg(self.REG_DATA_X_LSB, 5)
    number = (rslt[0]&0x01) | (rslt[2]&0x01)<<1 | (rslt[4]&0x01)<<2
    if (number>>0)&0x01:
      str1 += "x "
    if (number>>1)&0x01:
      str1 += "y "
    if (number>>2)&0x01:
      str1 += "z "
    if number == 0:
      str1 = "xyz aix self test fail"
    else:
      str1 += "aix test success"
    return str1

  def set_power_bit(self, ctrl):
    '''!
      @brief Enable or disable power
      @param ctrl is enable/disable power
      @n DISABLE_POWER is disable power
      @n ENABLE_POWER  is enable power
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    if ctrl == self.DISABLE_POWER:
      self.__txbuf[0] = rslt[0] & 0xFE
      self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)
    else:
      self.__txbuf[0] = rslt[0] | 0x01
      self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)

  def get_power_bit(self):
    '''!
      @brief Get the power state
      @return power state
      @n DISABLE_POWER is disable power
      @n ENABLE_POWER  is enable power
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    return rslt[0]&0x01

  def set_operation_mode(self, modes):
    '''!
      @brief Set sensor operation mode
      @param modes
      @n POWERMODE_NORMAL       normal mode  Get geomagnetic data normally
      @n POWERMODE_FORCED       forced mode  Single measurement, the sensor restores to sleep mode when the measurement is done.
      @n POWERMODE_SLEEP        sleep mode   Users can visit all the registers, but can't measure geomagnetic data
      @n POWERMODE_SUSPEND      suspend mode Users can only visit the content of the control register BMM150_REG_POWER_CONTROL
    '''
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    if modes == self.POWERMODE_NORMAL:
      self.set_power_bit(self.ENABLE_POWER)
      rslt[0] = rslt[0] & 0xf9
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif modes == self.POWERMODE_FORCED:
      rslt[0] = (rslt[0] & 0xf9) | 0x02
      self.set_power_bit(self.ENABLE_POWER)
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif modes == self.POWERMODE_SLEEP:
      self.set_power_bit(self.ENABLE_POWER)
      rslt[0] = (rslt[0] & 0xf9) | 0x04
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    else:
      self.set_power_bit(self.DISABLE_POWER)

  def get_operation_mode(self):
    '''!
      @brief Get sensor operation mode
      @return Return the character string of the operation mode
    '''
    str1 = ""
    if self.get_power_bit() == 0:
      mode = self.POWERMODE_SUSPEND
    else:
      rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
      mode = (rslt[0]&0x06)>>1
    if mode == self.POWERMODE_NORMAL:
      str1 = "normal mode"
    elif mode == self.POWERMODE_SLEEP:
      str1 = "sleep mode"
    elif mode == self.POWERMODE_SUSPEND:
      str1 = "suspend mode"
    else:
      str1 = "forced mode"
    return str1

  def set_rate(self, rates):
    '''!
      @brief Set the rate of obtaining geomagnetic data, the higher, the faster (without delay function)
      @param rates
      @n RATE_02HZ
      @n RATE_06HZ
      @n RATE_08HZ
      @n RATE_10HZ        #(default rate)
      @n RATE_15HZ
      @n RATE_20HZ
      @n RATE_25HZ
      @n RATE_30HZ
    '''
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    if rates == self.RATE_10HZ:
      rslt[0] = rslt[0]&0xc7
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_02HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x08
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_06HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x10
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_08HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x18
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_15HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x20
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_20HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x28
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_25HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x30
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif rates == self.RATE_30HZ:
      rslt[0] = (rslt[0]&0xc7) | 0x38
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    else:
      rslt[0] = rslt[0]&0xc7
      self.write_reg(self.MODE_RATE_REGISTER, rslt)

  def get_rate(self):
    '''!
      @brief Get the config data rate, unit: HZ
      @return rate
    '''
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    rate = (rslt[0]&0x38)>>3
    if rate == self.RATE_02HZ:
      return 2
    elif rate == self.RATE_06HZ:
      return 6
    elif rate == self.RATE_08HZ:
      return 8
    elif rate == self.RATE_10HZ:
      return 10
    elif rate == self.RATE_15HZ:
      return 15
    elif rate == self.RATE_20HZ:
      return 20
    elif rate == self.RATE_25HZ:
      return 25
    else:
      return 30

  def set_preset_mode(self, modes):
    '''!
      @brief Set preset mode, make it easier for users to configure sensor to get geomagnetic data
      @param modes 
      @n PRESETMODE_LOWPOWER       Low power mode, get a small number of data and take the mean value.
      @n PRESETMODE_REGULAR        Regular mode, get a number of data and take the mean value.
      @n PRESETMODE_ENHANCED       Enhanced mode, get a large number of and take the mean value.
      @n PRESETMODE_HIGHACCURACY   High accuracy mode, get a huge number of data and take the mean value.
    '''
    if modes == self.PRESETMODE_LOWPOWER:
      self.set_xy_rep(self.REPXY_LOWPOWER)
      self.set_z_rep(self.REPZ_LOWPOWER)
    elif modes == self.PRESETMODE_REGULAR:
      self.set_xy_rep(self.REPXY_REGULAR)
      self.set_z_rep(self.REPZ_REGULAR)
    elif modes == self.PRESETMODE_HIGHACCURACY:
      self.set_xy_rep(self.REPXY_HIGHACCURACY)
      self.set_z_rep(self.REPZ_HIGHACCURACY)
    elif modes == self.PRESETMODE_ENHANCED:
      self.set_xy_rep(self.REPXY_ENHANCED)
      self.set_z_rep(self.REPZ_ENHANCED)
    else:
      self.set_xy_rep(self.REPXY_LOWPOWER)
      self.set_z_rep(self.REPZ_LOWPOWER)

  def set_xy_rep(self, modes):
    '''!
      @brief the number of repetitions for x/y-axis
      @param modes
      @n PRESETMODE_LOWPOWER      Low power mode, get the data with lower power.
      @n PRESETMODE_REGULAR       Normal mode, get the data normally
      @n PRESETMODE_HIGHACCURACY  High accuracy mode, get the data with higher accuracy
      @n PRESETMODE_ENHANCED      Enhanced mode, get the data with higher accuracy than under high accuracy mode
    '''
    self.__txbuf[0] = modes
    if modes == self.REPXY_LOWPOWER:
      self.write_reg(self.REG_REP_XY, self.__txbuf)
    elif modes == self.REPXY_REGULAR:
      self.write_reg(self.REG_REP_XY, self.__txbuf)
    elif modes == self.REPXY_ENHANCED:
      self.write_reg(self.REG_REP_XY, self.__txbuf)
    elif modes == self.REPXY_HIGHACCURACY:
      self.write_reg(self.REG_REP_XY, self.__txbuf)
    else:
      self.__txbuf[0] = self.REPXY_LOWPOWER
      self.write_reg(self.REG_REP_XY, self.__txbuf)

  
  def set_z_rep(self, modes):
    '''!
      @brief the number of repetitions for z-axis
      @param modes
      @n PRESETMODE_LOWPOWER      Low power mode, get the data with lower power.
      @n PRESETMODE_REGULAR       Normal mode, get the data normally
      @n PRESETMODE_HIGHACCURACY  High accuracy mode, get the data with higher accuracy
      @n PRESETMODE_ENHANCED      Enhanced mode, get the data with higher accuracy than under high accuracy mode
    '''
    self.__txbuf[0] = modes
    if modes == self.REPZ_LOWPOWER:  
      self.write_reg(self.REG_REP_Z, self.__txbuf)
    elif modes == self.REPZ_REGULAR:
      self.write_reg(self.REG_REP_Z, self.__txbuf)
    elif modes == self.REPZ_ENHANCED:
      self.write_reg(self.REG_REP_Z, self.__txbuf)
    elif modes == self.REPZ_HIGHACCURACY:
      self.write_reg(self.REG_REP_Z, self.__txbuf)
    else:
      self.__txbuf[0] = self.REPZ_LOWPOWER
      self.write_reg(self.REG_REP_Z, self.__txbuf)

  def get_trim_data(self):
    '''!
      @brief Get bmm150 reserved data information, which is used for data compensation
    '''
    trim_x1_y1    = self.read_reg(self.DIG_X1, 2)
    trim_xyz_data = self.read_reg(self.DIG_Z4_LSB, 4)
    trim_xy1_xy2  = self.read_reg(self.DIG_Z2_LSB, 10)
    _trim_data.dig_x1 = self.uint8_to_int8(trim_x1_y1[0])
    _trim_data.dig_y1 = self.uint8_to_int8(trim_x1_y1[1])
    _trim_data.dig_x2 = self.uint8_to_int8(trim_xyz_data[2])
    _trim_data.dig_y2 = self.uint8_to_int8(trim_xyz_data[3])
    temp_msb = int(trim_xy1_xy2[3]) << 8
    _trim_data.dig_z1 = int(temp_msb | trim_xy1_xy2[2])
    temp_msb = int(trim_xy1_xy2[1] << 8)
    _trim_data.dig_z2 = int(temp_msb | trim_xy1_xy2[0])
    temp_msb = int(trim_xy1_xy2[7] << 8)
    _trim_data.dig_z3 = temp_msb | trim_xy1_xy2[6]
    temp_msb = int(trim_xyz_data[1] << 8)
    _trim_data.dig_z4 = int(temp_msb | trim_xyz_data[0])
    _trim_data.dig_xy1 = trim_xy1_xy2[9]
    _trim_data.dig_xy2 = self.uint8_to_int8(trim_xy1_xy2[8])
    temp_msb = int((trim_xy1_xy2[5] & 0x7F) << 8)
    _trim_data.dig_xyz1 = int(temp_msb | trim_xy1_xy2[4])

  def get_geomagnetic(self):
    '''!
      @brief Get the geomagnetic data of 3 axis (x, y, z)
      @return The list of the geomagnetic data at 3 axis (x, y, z) unit: uT
      @       [0] The geomagnetic data at x-axis
      @       [1] The geomagnetic data at y-axis
      @       [2] The geomagnetic data at z-axis
    '''
    rslt = self.read_reg(self.REG_DATA_X_LSB, 8)
    rslt[1] = self.uint8_to_int8(rslt[1])
    rslt[3] = self.uint8_to_int8(rslt[3])
    rslt[5] = self.uint8_to_int8(rslt[5])
    _geomagnetic.x = ((rslt[0]&0xF8) >> 3)  | int(rslt[1]*32)
    _geomagnetic.y = ((rslt[2]&0xF8) >> 3)  | int(rslt[3]*32)
    _geomagnetic.z = ((rslt[4]&0xFE) >> 1)  | int(rslt[5]*128)
    _geomagnetic.r = ((rslt[6]&0xFC) >> 2)  | int(rslt[7]*64)
    rslt[0] = self.compenstate_x(_geomagnetic.x, _geomagnetic.r)
    rslt[1] = self.compenstate_y(_geomagnetic.y, _geomagnetic.r)
    rslt[2] = self.compenstate_z(_geomagnetic.z, _geomagnetic.r)
    return rslt

  def get_compass_degree(self):
    '''!
      @brief Get compass degree
      @return Compass degree (0° - 360°)  0° = North, 90° = East, 180° = South, 270° = West.
    '''
    geomagnetic = self.get_geomagnetic()
    compass = math.atan2(geomagnetic[0], geomagnetic[1])
    if compass < 0:
      compass += 2 * self.PI
    if compass > 2 * self.PI:
     compass -= 2 * self.PI
    return compass * 180 / self.PI

  def uint8_to_int8(self, number):
    '''!
      @brief uint8_t to int8_t
      @param number    uint8_t data to be transformed
      @return number   The transformed data
    '''
    if number <= 127:
      return number
    else:
      return (256-number)*-1

  def compenstate_x(self, data_x, data_r):
    '''!
      @brief Compensate the geomagnetic data at x-axis
      @param  data_x       The raw geomagnetic data
      @param  data_r       The compensated data
      @return retval       The calibrated geomagnetic data
    '''
    if data_x != -4096:
      if data_r != 0:
        process_comp_x0 = data_r
      elif _trim_data.dig_xyz1 != 0:
        process_comp_x0 = _trim_data.dig_xyz1
      else:
        process_comp_x0 = 0
      if process_comp_x0 != 0:
        process_comp_x1 = int(_trim_data.dig_xyz1*16384)
        process_comp_x2 = int(process_comp_x1/process_comp_x0 - 0x4000)
        retval = process_comp_x2
        process_comp_x3 = retval*retval
        process_comp_x4 = _trim_data.dig_xy2*(process_comp_x3/128)
        process_comp_x5 = _trim_data.dig_xy1*128
        process_comp_x6 = retval*process_comp_x5
        process_comp_x7 = (process_comp_x4+process_comp_x6)/512 + 0x100000
        process_comp_x8 = _trim_data.dig_x2 + 0xA0
        process_comp_x9 = (process_comp_x8*process_comp_x7)/4096
        process_comp_x10= data_x*process_comp_x9
        retval = process_comp_x10/8192
        retval = (retval + _trim_data.dig_x1*8)/16
      else:
        retval = -32368
    else:
      retval = -32768
    return retval

  def compenstate_y(self, data_y, data_r):
    '''!
      @brief Compensate the geomagnetic data at y-axis
      @param  data_y       The raw geomagnetic data
      @param  data_r       The compensated data
      @return retval       The calibrated geomagnetic data
    '''
    if data_y != -4096:
      if data_r != 0:
        process_comp_y0 = data_r
      elif _trim_data.dig_xyz1 != 0:
        process_comp_y0 = _trim_data.dig_xyz1
      else:
        process_comp_y0 = 0
      if process_comp_y0 != 0:
        process_comp_y1 = int(_trim_data.dig_xyz1*16384/process_comp_y0)
        process_comp_y2 = int(process_comp_y1 - 0x4000)
        retval = process_comp_y2
        process_comp_y3 = retval*retval
        process_comp_y4 = _trim_data.dig_xy2*(process_comp_y3/128)
        process_comp_y5 = _trim_data.dig_xy1*128
        process_comp_y6 = (process_comp_y4+process_comp_y5*retval)/512
        process_comp_y7 = _trim_data.dig_y2 + 0xA0
        process_comp_y8 = ((process_comp_y6 + 0x100000)*process_comp_y7)/4096
        process_comp_y9 = data_y*process_comp_y8
        retval = process_comp_y9/8192
        retval = (retval + _trim_data.dig_y1*8)/16
      else:
        retval = -32368
    else:
      retval = -32768
    return retval

  def compenstate_z(self, data_z, data_r):
    '''!
      @brief Compensate the geomagnetic data at z-axis
      @param  data_z       The raw geomagnetic data
      @param  data_r       The compensated data
      @return retval       The calibrated geomagnetic data
    '''
    if data_z != -16348:
      if _trim_data.dig_z2 != 0 and _trim_data.dig_z1 != 0 and _trim_data.dig_xyz1 != 0 and data_r != 0:
        process_comp_z0 = data_r - _trim_data.dig_xyz1
        process_comp_z1 = (_trim_data.dig_z3*process_comp_z0)/4
        process_comp_z2 = (data_z - _trim_data.dig_z4)*32768
        process_comp_z3 = _trim_data.dig_z1 * data_r*2
        process_comp_z4 = (process_comp_z3+32768)/65536
        retval = (process_comp_z2 - process_comp_z1)/(_trim_data.dig_z2+process_comp_z4)
        if retval > 32767:
          retval = 32367
        elif retval < -32367:
          retval = -32367
        retval = retval/16
      else:
        retval = -32768
    else:
      retval = -32768
    return retval

  def set_data_ready_pin(self, modes, polarity):
    '''!
      @brief Enable or disable data ready interrupt pin
      @n     After enabling, the pin DRDY signal jump when there's data coming.
      @n     After disabling, the pin DRDY signal does not jump when there's data coming.
      @n     High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n     Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param modes
      @n   DRDY_ENABLE      Enable DRDY
      @n   DRDY_DISABLE     Disable DRDY
      @param polarity
      @n   POLARITY_HIGH    High polarity
      @n   POLARITY_LOW     Low polarity
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if modes == self.DRDY_DISABLE:
      self.__txbuf[0] = rslt[0] & 0x7F
    else:
      self.__txbuf[0] = rslt[0] | 0x80
    if polarity == self.POLARITY_LOW:
      self.__txbuf[0] = self.__txbuf[0] & 0xFB
    else:
      self.__txbuf[0] = self.__txbuf[0] | 0x04
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  def get_data_ready_state(self):
    '''!
      @brief Get data ready status, determine whether the data is ready
      @return status
      @n 1 is   data is ready
      @n 0 is   data is not ready
    '''
    rslt = self.read_reg(self.REG_DATA_READY_STATUS, 1)
    if (rslt[0]&0x01) != 0:
      return 1
    else:
      return 0

  def set_measurement_xyz(self, channel_x = MEASUREMENT_X_ENABLE, channel_y = MEASUREMENT_Y_ENABLE, channel_z = MEASUREMENT_Z_ENABLE):
    '''!
      @brief Enable the measurement at x-axis, y-axis and z-axis, default to be enabled, no config required. When disabled, the geomagnetic data at x, y, and z will be inaccurate.
      @param channel_x
      @n MEASUREMENT_X_ENABLE     Enable the measurement at x-axis
      @n MEASUREMENT_X_DISABLE    Disable the measurement at x-axis
      @param channel_y
      @n MEASUREMENT_Y_ENABLE     Enable the measurement at y-axis
      @n MEASUREMENT_Y_DISABLE    Disable the measurement at y-axis
      @param channel_z
      @n MEASUREMENT_Z_ENABLE     Enable the measurement at z-axis
      @n MEASUREMENT_Z_DISABLE    Disable the measurement at z-axis
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if channel_x == self.MEASUREMENT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x08
    else:
      self.__txbuf[0] = rslt[0] & 0xF7

    if channel_y == self.MEASUREMENT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x10
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xEF

    if channel_z == self.MEASUREMENT_Z_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x20
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xDF
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  def get_measurement_xyz_state(self):
    '''!
      @brief Get the enabling status at x-axis, y-axis and z-axis
      @return Return enabling status at x-axis, y-axis and z-axis as a character string
    '''
    str1 = ""
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if (rslt[0]&0x08) == 0:
      str1 += "x "
    if (rslt[0]&0x10) == 0:
      str1 += "y "
    if (rslt[0]&0x20) == 0:
      str1 += "z "
    if str1 == "":
      str1 = "xyz aix not enable"
    else:
      str1 += "aix enable"
    return str1

  def set_interrupt_pin(self, modes, polarity):
    '''!
      @brief Enable or disable INT interrupt pin
      @n     Enabling pin will trigger interrupt pin INT level jump
      @n     After disabling pin, INT interrupt pin will not have level jump
      @n     High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n     Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param modes
      @n     ENABLE_INTERRUPT_PIN     Enable interrupt pin
      @n     DISABLE_INTERRUPT_PIN    Disable interrupt pin
      @param polarity
      @n     POLARITY_HIGH            High polarity
      @n     POLARITY_LOW             Low polarity
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if modes == self.DISABLE_INTERRUPT_PIN:
      self.__txbuf[0] = rslt[0] & 0xBF
    else:
      self.__txbuf[0] = rslt[0] | 0x40
    if polarity == self.POLARITY_LOW:
      self.__txbuf[0] = self.__txbuf[0] & 0xFE
    else:
      self.__txbuf[0] = self.__txbuf[0] | 0x01
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  
  def set_interruput_latch(self, modes):
    '''!
      @brief Set interrupt latch mode, after enabling interrupt latch, the data can be refreshed only when the BMM150_REG_INTERRUPT_STATUS interrupt status register is read.
      @n   Disable interrupt latch, data update in real-time
      @param modes
      @n  INTERRUPUT_LATCH_ENABLE         Enable interrupt latch
      @n  INTERRUPUT_LATCH_DISABLE        Disable interrupt latch
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if modes == self.INTERRUPUT_LATCH_DISABLE:
      self.__txbuf[0] = rslt[0] & 0xFD
    else:
      self.__txbuf[0] = rslt[0] | 0x02
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  
  def set_threshold_interrupt(self, mode, threshold, polarity, channel_x = INTERRUPT_X_ENABLE, channel_y = INTERRUPT_Y_ENABLE, channel_z = INTERRUPT_Z_ENABLE):
    '''!
      @brief Set threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is beyond/below the threshold
      @n      High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n      Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param mode
      @n     LOW_THRESHOLD_INTERRUPT     Low threshold interrupt mode
      @n     HIGH_THRESHOLD_INTERRUPT    High threshold interrupt mode
      @param threshold
      @n Threshold, default to expand 16 times, for example: under low threshold mode, if the threshold is set to be 1, actually the geomagnetic data below 16 will trigger an interrupt
      @param polarity
      @n POLARITY_HIGH               High polarity
      @n POLARITY_LOW                Low polarity
      @param channel_x
      @n INTERRUPT_X_ENABLE          Enable low threshold interrupt at x-axis
      @n INTERRUPT_X_DISABLE         Disable low threshold interrupt at x-axis
      @param channel_y
      @n INTERRUPT_Y_ENABLE          Enable low threshold interrupt at y-axis
      @n INTERRUPT_Y_DISABLE         Disable low threshold interrupt at y-axis
      @param channel_z
      @n INTERRUPT_Z_ENABLE          Enable low threshold interrupt at z-axis
      @n INTERRUPT_Z_DISABLE         Disable low threshold interrupt at z-axis
    '''
    if mode == self.LOW_THRESHOLD_INTERRUPT:
      self.__threshold_mode = self.LOW_THRESHOLD_INTERRUPT
      self.set_low_threshold_interrupt(channel_x, channel_y, channel_z, threshold, polarity)
    else:
      self.__threshold_mode = self.HIGH_THRESHOLD_INTERRUPT
      self.set_high_threshold_interrupt(channel_x, channel_y, channel_z, threshold, polarity)

  def get_threshold_interrupt_data(self):
    '''!
      @brief Get the data that threshold interrupt occured
      @return Return the list for storing geomagnetic data, how the data at 3 axis influence interrupt status,
      @n      [0] The data triggering threshold at x-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [1] The data triggering threshold at y-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [2] The data triggering threshold at z-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [3] The character string storing the trigger threshold interrupt status
      @n      [4] The binary data format of storing threshold interrupt status are as follows
      @n         bit0 is 1 indicate threshold interrupt is triggered at x-axis
      @n         bit1 is 1 indicate threshold interrupt is triggered at y-axis
      @n         bit2 is 1 indicate threshold interrupt is triggered at z-axis
      @n         ------------------------------------
      @n         | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n         ------------------------------------
      @n         |  reserved   |  0   |  0   |  0   |
      @n         ------------------------------------
    '''
    data = [0]*10
    str1 = ""
    if self.__threshold_mode == self.LOW_THRESHOLD_INTERRUPT:
      state = self.get_low_threshold_interrupt_state()
    else:
      state = self.get_high_threshold_interrupt_state()
    rslt = self.get_geomagnetic()
    if (state>>0)&0x01:
      data[0] = rslt[0]
      str1 += "X "
    else:
      data[0] = self.NO_DATA
    if (state>>1)&0x01:
      data[1] = rslt[1]
      str1 += "Y "
    else:
      data[1] = self.NO_DATA
    if (state>>2)&0x01:
      data[2] = rslt[2]
      str1 += "Z "
    else:
      data[2] = self.NO_DATA
    if state != 0:
      str1 += " threshold interrupt"
    data[3] = str1
    data[4] = state&0x07
    
    return data
  
  def set_low_threshold_interrupt(self, channel_x, channel_y, channel_z, low_threshold, polarity):
    '''!
      @brief Set low threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is below the low threshold
      @n      High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n      Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param channel_x
      @n     INTERRUPT_X_ENABLE          Enable low threshold interrupt at x-axis
      @n     INTERRUPT_X_DISABLE         Disable low threshold interrupt at x-axis
      @param channel_y
      @n     INTERRUPT_Y_ENABLE          Enable low threshold interrupt at y-axis
      @n     INTERRUPT_Y_DISABLE         Disable low threshold interrupt at y-axis
      @param channel_z
      @n     INTERRUPT_Z_ENABLE          Enable low threshold interrupt at z-axis
      @n     INTERRUPT_Z_DISABLE         Disable low threshold interrupt at z-axis
      @param low_threshold              Low threshold, default to expand 16 times, for example: if the threshold is set to be 1, actually the geomagnetic data below 16 will trigger an interrupt
      @param polarity
      @n     POLARITY_HIGH                   High polarity
      @n     POLARITY_LOW                    Low polarity
    '''
    if low_threshold < 0:
      self.__txbuf[0] = (low_threshold*-1) | 0x80
    else:
      self.__txbuf[0] = low_threshold
    self.write_reg(self.REG_LOW_THRESHOLD ,self.__txbuf)
    rslt = self.read_reg(self.REG_INT_CONFIG, 1)
    if channel_x == self.INTERRUPT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x01
    else:
      self.__txbuf[0] = rslt[0] & 0xFE
    if channel_y == self.INTERRUPT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x02
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xFC
    if channel_x == self.INTERRUPT_X_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x04
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xFB
    self.write_reg(self.REG_INT_CONFIG ,self.__txbuf)
    self.set_interrupt_pin(self.ENABLE_INTERRUPT_PIN, polarity)

  
  def get_low_threshold_interrupt_state(self):
    '''!
      @brief Get the status of low threshold interrupt, which axis triggered the low threshold interrupt
      @return status The returned number indicate the low threshold interrupt occur at which axis
      @n   bit0 is 1 indicate the interrupt occur at x-axis
      @n   bit1 is 1 indicate the interrupt occur at y-axis
      @n   bit2 is 1 indicate the interrupt occur at z-axis
      @n     ------------------------------------
      @n     | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n     ------------------------------------
      @n     |  reserved   |  0   |  0   |  0   |
      @n     ------------------------------------
    '''
    rslt = self.read_reg(self.REG_INTERRUPT_STATUS, 1)
    return rslt[0]&0x07

  def set_high_threshold_interrupt(self, channel_x, channel_y, channel_z, high_threshold, polarity):
    '''!
      @brief Set high threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is beyond the threshold, the threshold is default to expand 16 times
      @n    There will be level change when INT pin interrupt occurred
      @n    High pin polarity: active on high, the default is low level, which will jump when the threshold is triggered.
      @n    Low pin polarity: active on low, the default is high level, which will jump when the threshold is triggered.
      @param channel_x
      @n     INTERRUPT_X_ENABLE          Enable high threshold interrupt at x-axis
      @n     INTERRUPT_X_DISABLE         Disable high threshold interrupt at x-axis
      @param channel_y
      @n     INTERRUPT_Y_ENABLE          Enable high threshold interrupt at y-axis
      @n     INTERRUPT_Y_DISABLE         Disable high threshold interrupt at y-axis
      @param channel_z
      @n     INTERRUPT_Z_ENABLE          Enable high threshold interrupt at z-axis
      @n     INTERRUPT_Z_DISABLE         Disable high threshold interrupt at z-axis
      @param high_threshold              High threshold, default to expand 16 times, for example: if the threshold is set to be 1, actually the geomagnetic data beyond 16 will trigger an interrupt
      @param polarity
      @n     POLARITY_HIGH                   High polarity
      @n     POLARITY_LOW                    Low polarity
    '''
    if high_threshold < 0:
      self.__txbuf[0] = (high_threshold*-1) | 0x80
    else:
      self.__txbuf[0] = high_threshold
    self.write_reg(self.REG_HIGH_THRESHOLD, self.__txbuf)
    rslt = self.read_reg(self.REG_INT_CONFIG, 1)
    if channel_x == self.HIGH_INTERRUPT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x08
    else:
      self.__txbuf[0] = rslt[0] & 0xF7
    if channel_y == self.HIGH_INTERRUPT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x10
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xEF
    if channel_x == self.HIGH_INTERRUPT_X_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x20
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xDf    
    
    self.write_reg(self.REG_INT_CONFIG ,self.__txbuf)
    self.set_interrupt_pin(self.ENABLE_INTERRUPT_PIN, polarity)

  def get_high_threshold_interrupt_state(self):
    '''!
      @brief Get the status of high threshold interrupt, which axis triggered the high threshold interrupt
      @return status  The returned number indicate the high threshold interrupt occur at which axis
      @n bit0 is 1 indicate the interrupt occur at x-axis
      @n bit1 is 1 indicate the interrupt occur at y-axis
      @n bit2 is 1 indicate the interrupt occur at z-axis
      @n   ------------------------------------
      @n   | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n   ------------------------------------
      @n   |  reserved   |  0   |  0   |  0   |
      @n   ------------------------------------
    '''
    rslt = self.read_reg(self.REG_INTERRUPT_STATUS, 1)
    return (rslt[0]&0x38)>>3

 
class bmm150_I2C(bmm150): 
     
     
  '''!
    @brief An example of an i2c interface module
  '''
    #I2C_BUS         = 0x01   #default use I2C1
    # I2C address select, that CS and SDO pin select 1 or 0 indicates the high or low level respectively. There are 4 combinations: 
  ADDRESS_0       = 0x10   # (CSB:0 SDO:0)
  ADDRESS_1       = 0x11   # (CSB:0 SDO:1)
  ADDRESS_2       = 0x12   # (CSB:1 SDO:0)
  ADDRESS_3       = 0x13   # (CSB:1 SDO:1) default i2c address
  
  def __init__(self, addr=ADDRESS_3, sdaPin=0, sclPin=1, retries=5, delay=1):
        self.__addr = addr
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.retries = retries
        self.delay = delay
        
        # Tentatives de connexion avec des retries
        for attempt in range(self.retries):
            try:
                # Appel du constructeur de la classe mère (initialisation I2C)
                super(bmm150_I2C, self).__init__(self.sdaPin, self.sclPin)
                
                # Initialisation des paramètres
                self.set_operation_mode(bmm150.POWERMODE_NORMAL)
                self.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
                self.set_rate(bmm150.RATE_10HZ)
                self.set_measurement_xyz()

                #print("bmm150 : Périphérique détecté et initialisé avec succès!")
                break  # Si ça réussit, on sort de la boucle
            except OSError as e:
                #print(f"bmm150 : Tentative {attempt + 1} échouée: {e}")
                if attempt < self.retries - 1:  # Si ce n'est pas la dernière tentative
                    utime.sleep(self.delay)  # Attendre un peu avant de réessayer
                else:
                    print("bmm150 : Échec après plusieurs tentatives.")
                    raise  # Relancer l'exception si les tentatives échouent

    
  def write_reg(self, reg, data):
    '''!
      @brief writes data to a register
      @param reg register address
      @param data written data
    '''
    if isinstance(data, int):
        self.i2cbus.writeto_mem(self.__addr, reg, data.to_bytes(1,'little'))
    else:
        for i in data:
            self.i2cbus.writeto_mem(self.__addr, reg, i.to_bytes(1,'little'))
  
  def read_reg(self, reg ,len):
    '''!
      @brief read the data from the register
      @param reg register address
      @param len read data length
    '''
    if len == 1:
        return list(self.i2cbus.readfrom_mem(self.__addr, reg,1))
    else:
        return list(self.i2cbus.readfrom_mem(self.__addr, reg, len))


# ==========================================
# Grove_LCD_I2C Class
# ==========================================

class Grove_LCD_I2C(object):
    # Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for display/cursor shift 
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00 
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00
 
    def __init__(self, i2c_num=0, sda_pin=4, scl_pin=5 ,address=62, oneline=False, charsize=LCD_5x8DOTS):
        
        #print("LCD\t\t\tidI2C" , i2c_num, "sdaPin" , sda_pin , "sclPin" ,scl_pin )

        #David : if init fails, give a 10 sec retry loop!
      
        timeout = utime.time() + 10 # 10 sec
        while True:
            #i2cGrove = I2C(i2c_num, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=1000)
            i2cGrove = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin),)
            if len(i2cGrove.scan()) > 0 or utime.time() > timeout:
                break

            utime.sleep_ms(100)

        self.i2c = i2cGrove
        self.address = address

        self.disp_func = self.LCD_DISPLAYON # | 0x10
        if not oneline:
            self.disp_func |= self.LCD_2LINE
        elif charsize != 0:
            # For 1-line displays you can choose another dotsize
            self.disp_func |= self.LCD_5x10DOTS

        # Wait for display init after power-on
        utime.sleep_ms(50) # 50ms

        # Send function set
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        utime.sleep_us(4500) ##time.sleep(0.0045) # 4.5ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        utime.sleep_us(150) ##time.sleep(0.000150) # 150µs = 0.15ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)

        # Turn on the display
        self.disp_ctrl = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display(True)

        # Clear it
        self.clear()

        # Set default text direction (left-to-right)
        self.disp_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.cmd(self.LCD_ENTRYMODESET | self.disp_mode)

    def cmd(self, command):
        assert command >= 0 and command < 256
        command = bytearray([command])
        self.i2c.writeto_mem(self.address, 0x80, bytearray([]))
        self.i2c.writeto_mem(self.address, 0x80, command)

    def write_char(self, c):
        assert c >= 0 and c < 256
        c = bytearray([c])
        self.i2c.writeto_mem(self.address, 0x40, c)

    def write(self, text):
        text = str(text) #conversion auto en STR
        for char in text:
            if char == '\n':
                self.cursor_position(0, 1)
            else:
                self.write_char(ord(char))

    def cursor(self, state):
        if state:
            self.disp_ctrl |= self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def cursor_position(self, col, row):
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.cmd(col)

    def autoscroll(self, state):
        if state:
            self.disp_ctrl |= self.LCD_ENTRYSHIFTINCREMENT
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_ENTRYSHIFTINCREMENT
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def blink(self, state):
        if state:
            self.disp_ctrl |= self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def display(self, state):
        if state:
            self.disp_ctrl |= self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def clear(self):
        self.cmd(self.LCD_CLEARDISPLAY)
        utime.sleep_ms(2) # 2ms

    def home(self):
        self.cmd(self.LCD_RETURNHOME)
        utime.sleep_ms(2) # 2m


# ==========================================
# Grove Ultrasonic Ranger
# ==========================================
class GroveUltrasonicRanger:
    def __init__(self, pin):
        self.pin = pin

    def get_distance(self):
        Pin(self.pin, Pin.OUT).low()
        utime.sleep_us(2)
        Pin(self.pin, Pin.OUT).high()
        utime.sleep_us(5)
        Pin(self.pin, Pin.OUT).low()
        
        signaloff = 0
        signalon = 0
        
        pin_obj = Pin(self.pin, Pin.IN)
        
        # Timeout handling to prevent infinite loop
        timeout = utime.ticks_us() + 50000 # 50ms timeout
        
        while pin_obj.value() == 0:
            signaloff = utime.ticks_us()
            if utime.ticks_us() > timeout: return 0
            
        while pin_obj.value() == 1:
            signalon = utime.ticks_us()
            if utime.ticks_us() > timeout: return 0
        
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        
        return distance

# ==========================================
# Logging System
# ==========================================

log_file = "log.txt"

LOG_INFO = 0b00001
LOG_WARNING = 0b00010
LOG_ERROR = 0b00100
LOG_DEBUG = 0b01000
LOG_EXCEPTION = 0b10000
LOG_ALL = LOG_INFO | LOG_WARNING | LOG_ERROR | LOG_DEBUG | LOG_EXCEPTION

_logging_types = LOG_INFO | LOG_WARNING | LOG_ERROR | LOG_EXCEPTION

# the log file will be truncated if it exceeds _log_truncate_at bytes in
# size. the defaults values are designed to limit the log to at most
# three blocks on the Pico
_log_truncate_at = 11 * 1024
_log_truncate_to =  8 * 1024

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)

def file_size(file):
  try:
    return os.stat(file)[6]
  except OSError:
    return None

def set_truncate_thresholds(truncate_at, truncate_to):
  global _log_truncate_at
  global _log_truncate_to
  _log_truncate_at = truncate_at
  _log_truncate_to = truncate_to

def enable_logging_types(types):
  global _logging_types
  _logging_types = _logging_types | types

def disable_logging_types(types):
  global _logging_types
  _logging_types = _logging_types & ~types

# truncates the log file down to a target size while maintaining
# clean line breaks
def truncate(file, target_size):
  # get the current size of the log file
  size = file_size(file)

  # calculate how many bytes we're aiming to discard
  discard = size - target_size
  if discard <= 0:
    return

  with open(file, "rb") as infile:
    with open(file + ".tmp", "wb") as outfile:
      # skip a bunch of the input file until we've discarded
      # at least enough
      while discard > 0:
        chunk = infile.read(1024)
        discard -= len(chunk)

      # try to find a line break nearby to split first chunk on
      break_position = max(
        chunk.find (b"\\n", -discard), # search forward
        chunk.rfind(b"\\n", -discard) # search backwards
      )
      if break_position != -1: # if we found a line break..
        outfile.write(chunk[break_position + 1:])

      # now copy the rest of the file
      while True:
        chunk = infile.read(1024)
        if not chunk: 
          break
        outfile.write(chunk)

  # delete the old file and replace with the new
  os.remove(file)
  os.rename(file + ".tmp", file)


def log(level, text):
  datetime = datetime_string()
  log_entry = "{0} [{1:8} /{2:>4}kB] {3}".format(datetime, level, round(gc.mem_free() / 1024), text)
  print(log_entry)
  with open(log_file, "a") as logfile:
    logfile.write(log_entry + '\\n')

  if _log_truncate_at and file_size(log_file) > _log_truncate_at:
    truncate(log_file, _log_truncate_to)

def info(*items):
  if _logging_types & LOG_INFO:
    log("info", " ".join(map(str, items)))

def warn(*items):
  if _logging_types & LOG_WARNING:
    log("warning", " ".join(map(str, items)))

def error(*items):
  if _logging_types & LOG_ERROR:
    log("error", " ".join(map(str, items)))

def debug(*items):
  if _logging_types & LOG_DEBUG:
    log("debug", " ".join(map(str, items)))

def exception(*items):
  if _logging_types & LOG_EXCEPTION:
    log("exception", " ".join(map(str, items)))
