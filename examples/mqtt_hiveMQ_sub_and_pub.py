from mqtt import MQTTClientSimple
from fasapico import *
from machine import Timer

ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")

def on_message_callback(topic,msg):
    print("recu >>",topic,msg)

#merci de remplacer "DavidFasani" , sinon on va se faire jeter par le serveur
clientMQTT = MQTTClientSimple(client_id="DavidFasani", server="broker.hivemq.com")
clientMQTT.set_callback(on_message_callback)  #que doit-on faire à reception d'un message ? Appeler la fonction on_message_callback()
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
    print("Je publie sur quel topic ?")
    topic = input()
    print("Quel message ?")
    msg = input()
    clientMQTT.publish( topic , msg)
