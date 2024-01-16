from mqtt import TBDeviceMqttClient
from fasapico import *
from machine import Pin

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

led = Pin("LED")

# Callback for server RPC requests
# cette fonction est appelée lorsque l'utilisateur agit dans le dashboard
def rpc_request_callback(client, request_id, request_body):
    print( str(request_id)  , str(request_body))  
    # --
    # -- C EST ICI QU IL FAUT MODIFIER LE CODE
    # --
    
# Connect to ThingsBoard
client = TBDeviceMqttClient('demo.thingsboard.io', access_token='cleTopSecreteNePasDiffuser')

#set callback for rpc resquests
client.set_server_side_rpc_request_handler(rpc_request_callback)

# Connecting to ThingsBoard
client.connect()

while True :
    client.check_msg()

# Disconnecting from ThingsBoard
client.disconnect()
