#
# Executer ce script pour installer micropython-phew sur votre Pico W.
# 


import mip, network, time

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30, debug=False):
    statuses = {
        network.STAT_IDLE: "idle",
        network.STAT_CONNECTING: "connecting",
        network.STAT_WRONG_PASSWORD: "wrong password",
        network.STAT_NO_AP_FOUND: "access point not found",
        network.STAT_CONNECT_FAIL: "connection failed",
        network.STAT_GOT_IP: "got ip address"
    }


    wlan = network.WLAN(network.STA_IF)
    
    # 🔄 Réinitialisation propre
    wlan.active(False)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)
    
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    status = wlan.status()

    if debug:
        print(f"Tentative de connexion à {ssid}...")
    
    while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
        status = wlan.status()
        if debug:
            print(f"Statut WiFi mis à jour : {statuses.get(status, 'inconnu')}")
        time.sleep(1)

    if wlan.status() != network.STAT_GOT_IP:
        if debug:
            print(f"Échec de la connexion à {ssid} : {statuses.get(wlan.status(), wlan.status())}")
        raise RuntimeError(f"Network connection to {ssid} failed")

    ifconfig_data = wlan.ifconfig()
    if debug:
        print(f"Configuration réseau complète : {ifconfig_data}")
        print("Attente pour stabilisation du WiFi...")
    
    time.sleep(1)
    return ifconfig_data[0]


# --- Connexion au WiFi ---
# --> Modifier le mot de passe si nécessaire
print("Connexion au réseau WiFi...")
ip = connect_to_wifi(ssid = "Icam_IOT", password = "V@nn3s2026")

print("\nConnecté ! Adresse IP :", ip)

# --- Installation avec mip ---
print("Installation de micropython-phew avec mip...")
mip.install("github:pimoroni/phew")
print("Installation terminée.")
