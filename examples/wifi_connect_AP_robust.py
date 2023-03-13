import network
import time

#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
