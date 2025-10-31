from fasapico import *
from mqtt import *  

# Connexion au wifi
ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")
print(ip)

# connection au broker MQTT 
clientMQTT = MQTTClientSimple(client_id="monPrenomMonNom", server="mqtt.dev.icam.school", port=1883)
clientMQTT.connect()

# publication d'un message sur un topic qui commence par bzh/mecatro/dashboard/...
clientMQTT.publish(topic="bzh/mecatro/dashboard/miamconnect/eau" , msg="21 cl") #tu peux changer de topic et de msg !
clientMQTT.disconnect()

print('fini')