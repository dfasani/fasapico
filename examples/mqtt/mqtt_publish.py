# TU PEUX UTILISER MYMQTT POUR VOIR PASSER TES MESSAGES
# https://docs.google.com/document/d/1mkWo8zZq7YhfvuBroEKIhkHOfYhrmuTnTPge-tpJIf8/edit#heading=h.e8io5gb96871


from fasapico import *

# ClientMQTT prend en charge la connexion WiFi et MQTT par défaut
clientMQTT = ClientMQTT()

clientMQTT.publish("bzh/iot/demo/maquette/a3", "bientot le WE !") # tu peux changer de topic et de msg !

print("deja fini !!!")
