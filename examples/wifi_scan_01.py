import network

wlan = network.WLAN(network.STA_IF)  # Carte WiFi en mode station
wlan.active(True)
network_list = wlan.scan()  # Liste des réseaux WiFi détectés

for net in network_list:
    ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]  # Décodage du SSID si nécessaire
    bssid = ":".join(["%02x" % b for b in net[1]])  # Formatage du BSSID
    channel = net[2]
    rssi = net[3]
    security = net[4]
    hidden = "Oui" if net[5] else "Non"
    
    print(f"SSID: {ssid}, BSSID: {bssid}, Canal: {channel}, RSSI: {rssi} dBm, Sécurité: {security}, Caché: {hidden}")

