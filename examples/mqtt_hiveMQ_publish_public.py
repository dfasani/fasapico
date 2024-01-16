from mqtt import MQTTClientSimple
from fasapico import *

ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")


#												#
#	A TOI DE REMPLACER "tonPrenomTonNomIci"		#
#	SINON ON SE FAIT JETER PAR LE SERVEUR !		#
#												#

#merci de remplacer "tonPrenomTonNomIci" , sinon on va se faire jeter par le serveur
clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="broker.hivemq.com")
clientMQTT.connect()
clientMQTT.publish(topic="bretagne/a3" , msg="bientot le WE !") #tu peux changer de topic et de msg !
clientMQTT.disconnect()

print("deja fini !!!")

# TU PEUX ALLER SUR https://www.hivemq.com/demos/websocket-client/  pour voir ton message passer !
