# TU PEUX UTILISER MYMQTT POUR VOIR PASSER TES MESSAGES
# https://docs.google.com/document/d/1mkWo8zZq7YhfvuBroEKIhkHOfYhrmuTnTPge-tpJIf8/edit#heading=h.e8io5gb96871


from fasapico import *
import secrets

ip = connect_to_wifi()


#												#
#	A TOI DE REMPLACER "tonPrenomTonNomIci"		#
#	SINON ON SE FAIT JETER PAR LE SERVEUR !		#
#												#

#merci de remplacer "tonPrenomTonNomIci" , sinon on va se faire jeter par le serveur
clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="mqtt.dev.icam.school", ssl=True)
clientMQTT.connect()
clientMQTT.publish(topic="bzh/iot/demo/maquette/a3" , msg="bientot le WE !") #tu peux changer de topic et de msg !
clientMQTT.disconnect()

print("deja fini !!!")
