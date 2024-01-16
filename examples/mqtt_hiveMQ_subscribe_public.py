from mqtt import MQTTClientSimple
from fasapico import *

ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")

#on dit que c'est un callback : cette fonction est donc appelée automatiquement a chaque reception de msg
def on_message_callback(topic,msg):
    print(topic,msg)
    
#merci de remplacer "tonPrenomTonNomIci" , sinon on va se faire jeter par le serveur
clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="broker.hivemq.com")
clientMQTT.connect() #start connection
clientMQTT.set_callback(on_message_callback) #a chaque evenement, on appelle la fonction on_message_callback()
clientMQTT.subscribe("bretagne/a3") #on s'abonne a bretagne/a3
clientMQTT.subscribe("toulouse/a3") #on s'abonne a toulouse/a3
clientMQTT.subscribe("lille/a3") #on s'abonne a lille/a3

while True :
    clientMQTT.wait_msg() #on regarde la boite aux lettres si un msg est arrivé
