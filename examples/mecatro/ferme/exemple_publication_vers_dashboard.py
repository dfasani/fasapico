from fasapico import *
import secrets

# Connexion au wifi
ip = connect_to_wifi()
print(ip)

# connection au broker MQTT 
clientMQTT = MQTTClientSimple(client_id="monPrenomMonNom", server="mqtt.dev.icam.school", ssl=True)
clientMQTT.connect()

# publication d'un message sur un topic qui commence par bzh/mecatro/dashboard/...
clientMQTT.publish(topic="bzh/mecatro/dashboard/miamconnect/eau" , msg="21 cl") #tu peux changer de topic et de msg !
clientMQTT.disconnect()

print('fini')