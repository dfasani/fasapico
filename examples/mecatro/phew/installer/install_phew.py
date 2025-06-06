import mip
from fasapico import *

# --- Connexion au WiFi ---
# --> a toi de changer le mot de passe si necessaire
print("Connexion au réseau WiFi...")
ip = connect_to_wifi(ssid = "icam_iot", password = "Summ3#C@mp2022")


print("\nConnecté ! Adresse IP :", ip)

# --- Installation avec mip ---
print("Installation de micropython-phew avec mip...")
mip.install("github:pimoroni/phew")
print("Installation terminée.")

