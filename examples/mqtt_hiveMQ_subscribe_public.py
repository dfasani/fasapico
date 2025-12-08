from fasapico import *
import secrets
ip = connect_to_wifi()

#on dit que c'est un callback : cette fonction est donc appelée automatiquement a chaque reception de msg
def on_message_callback(topic,msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print("recu >>",topic,msg)
    
#merci de remplacer "tonPrenomTonNomIci" , sinon on va se faire jeter par le serveur
clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="mqtt.dev.icam.school", ssl=True)
clientMQTT.connect() #start connection
clientMQTT.set_callback(on_message_callback) #a chaque evenement, on appelle la fonction on_message_callback()
clientMQTT.subscribe("bzh/iot/demo/maquette/a3") #on s'abonne a bzh/iot/demo/maquette/a3

while True :
    clientMQTT.wait_msg() #on regarde la boite aux lettres si un msg est arrivé
    #n'ajoute pas de code ici stp --> c'est la fonction on_message_callback() qu'on va completer
