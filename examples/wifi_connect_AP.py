import network
import time

#change si necessaire
WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

wlan = network.WLAN(network.STA_IF) #carte reseau en mode STATION
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

while not wlan.isconnected() and wlan.status() >= 0:
    print("J'essaie de me connecter...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    time.sleep(1)

print(wlan.ifconfig())
print("C'est bon ! Mon adresse IP est" , wlan.ifconfig()[0])
