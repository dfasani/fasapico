import network

# Initialiser l'interface Wi-Fi en mode station
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Récupérer l'adresse MAC sous forme de bytes
mac = wlan.config('mac')

# Formater l'adresse MAC : chaque octet en hexadécimal, majuscules, séparé par des :
mac_address = ':'.join('{:02X}'.format(b) for b in mac)

print("Adresse MAC :", mac_address)
