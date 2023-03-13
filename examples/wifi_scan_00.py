import network

wlan = network.WLAN(network.STA_IF) #  carte WiFi en mode station
wlan.active(True)
networkList = wlan.scan() # list de tuples de 6 champs : ssid, bssid, channel, RSSI, security, hidden

print(networkList) #affiche la liste