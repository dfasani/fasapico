# Exemple de publication MQTT avec le flag RETAIN
# Le flag "retain" (rétention) permet de dire au broker de conserver le dernier message envoyé sur ce topic.
# Ainsi, tout nouveau client qui s'abonnera à ce topic recevra immédiatement ce dernier message,
# même s'il a été envoyé avant que le client ne se connecte.

from fasapico import *

# ClientMQTT prend en charge la connexion WiFi et MQTT
clientMQTT = ClientMQTT(
    broker="mqtt.dev.icam.school",
    wifi_ssid="icam_iot",
    wifi_password="Summ3#C@mp2022"
)
clientMQTT.check_connection()

# Envoi du message avec le paramètre retain=True
clientMQTT.publish("bzh/iot/demo/maquette/a3_retain", "Message conservé par le broker !", retain=True) 

print("Message publié avec le flag retain activé !")
