from machine import *
from fasapico import *

def on_message_callback(topic,msg):
    print(f"Message reçu >> Topic : '{topic}' | Contenu : '{msg}'")

clientMQTT = ClientMQTT(
    broker="mqtt.dev.icam.school",
    wifi_ssid="icam_iot",
    wifi_password="Summ3#C@mp2022",
    callback=on_message_callback
)
# La méthode check_connection se charge aussi de nous connecter au WiFi par défaut
clientMQTT.check_connection()

print()
print("Je m'abonne a quel topic ?")
topic = input()
clientMQTT.subscribe(topic)

def timer_callback(data):
    clientMQTT.check_msg() #on releve la boite aux lettres
    
#ce timer appelle timer_callback() toutes les 100ms en arriere plan, on a plus besoin de gérer les appels =)
Timer(mode=Timer.PERIODIC, period=100, callback=timer_callback)

#Je demande en boucle
while True :
    print()
    print("Je publie sur quel topic ?")
    topic = input()
    print("Quel message ?")
    msg = input()
    clientMQTT.publish( topic , msg)




