import network
import time
import usocket as socket
import urequests
import json
import ubinascii
from machine import Timer

from .utils import warn, error, info, debug, decode_bytes

# ==========================================
# Network Utilities
# ==========================================

WIFI_SSID = "icam_iot"
WIFI_PWD = "Summ3#C@mp2022"

def is_connected_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid=None, password=None, timeout_seconds=30, debug=False):
    ssid = ssid or WIFI_SSID
    password = password or WIFI_PWD

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
def access_point(ssid, password=None):
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid)
    if password:
        wlan.config(password=password)
    else:
        wlan.config(security=0)  # disable password
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

# ==========================================
# MQTT Classes
# ==========================================
import ustruct as struct
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

def manage_mqtt_connection(client, server_broker, client_id, topic_cmd, callback, port=1883):
    """
    Gère la connexion WiFi et MQTT.
    Retourne l'objet client MQTT (connecté ou None si échec).
    """
    # 1. Check WiFi
    if not is_connected_to_wifi():
        warn("WiFi perdu. Tentative de reconnexion auto via configuration par défaut...")
        try:
            connect_to_wifi()  # Utilise les valeurs par défaut
        except Exception as e:
            error(f"Échec reconnexion WiFi: {e}")
            return None

    # 1c. Check Internet (Optionnel mais recommandé)
    if not check_internet_connection():
        error("Pas d'accès internet (Ping fail).")
        return None

    # 2. Check MQTT existant
    if client:
        try:
            client.ping()
            return client  # Tout va bien
        except:
            error("Lien MQTT mort.")
            client = None  # On force la reconnexion

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
            error(f"Échec Connexion MQTT: {e}")
            return None

    return client

class ClientMQTT:
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