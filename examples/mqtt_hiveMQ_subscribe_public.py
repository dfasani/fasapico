from mqtt import MQTTClientSimple
from phew import connect_to_wifi

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

def on_message_callback(topic,msg):
    print(topic,msg)
    
clientMQTT = MQTTClientSimple(client_id=b"tonPrenomTonNomIci", server="broker.hivemq.com")
clientMQTT.connect() #start connection
clientMQTT.set_callback(on_message_callback) #a chaque evenement, on appelle la fonction on_message_callback()
clientMQTT.subscribe("bretagne/a3") #on s'abonne a bretagne/a3

while True :
    c.wait_msg() #on regarde la boite aux lettres si un msg est arrivé