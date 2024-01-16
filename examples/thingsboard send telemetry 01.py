from mqtt import TBDeviceMqttClient
from fasapico import *

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

#     
#    / \
#   / | \
#  /  .  \      change la valeur de access_token !
# / _ _ _ \
#
# 
# On se connecte au serveur demo.thingsboard.io
client = TBDeviceMqttClient(host='demo.thingsboard.io', access_token='uneCleSecreteQueTuChange')

# Connecting to ThingsBoard
client.connect()

# Sending telemetry
telemetry = {'temperature': 11.9, 'enabled': False, 'name': 'Fasani'}
client.send_telemetry(telemetry)

# Disconnecting from ThingsBoard
client.disconnect()
