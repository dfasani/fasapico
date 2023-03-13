from mqtt import MQTTClientSimple
from phew import connect_to_wifi
from time import sleep
from machine import Timer

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

def on_message_callback(topic,msg):
    print("recu >>",topic,msg)

clientMQTT = MQTTClientSimple(client_id="DavidFasani", server="broker.hivemq.com")
clientMQTT.set_callback(on_message_callback)
clientMQTT.connect()

print("Je m'abonne a quel topic ?")
topic = input()
clientMQTT.subscribe(topic)

def timer_callback(data):
    clientMQTT.check_msg() #on releve la boite aux lettres
    
#ce timer appelle timer_callback() toutes les 100ms en arriere plan, on a plus besoin de gérer les appels =)
Timer(mode=Timer.PERIODIC, period=100, callback=timer_callback)

#Je demande en boucle
while True :
    print("Quel topic ?")
    topic = input()
    print("Quel message ?")
    msg = input()
    clientMQTT.publish( topic , msg)