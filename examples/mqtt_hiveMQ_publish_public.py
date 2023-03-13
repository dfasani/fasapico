from mqtt import MQTTClientSimple
from phew import connect_to_wifi
from time import sleep

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

clientMQTT = MQTTClientSimple(client_id="tonPrenomTonNomIci", server="broker.hivemq.com")
clientMQTT.connect()
clientMQTT.publish(topic="bretagne/a3" , msg="bientot le WE !") #tu peux changer de topic et de msg !
clientMQTT.disconnect()
