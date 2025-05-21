# Installation de la bibliothèque Phew pour MicroPython

Ce script permet de connecter automatiquement un microcontrôleur équipé de MicroPython à un réseau WiFi, puis d'installer la bibliothèque [Phew](https://github.com/pimoroni/phew) depuis GitHub à l'aide de l'outil `mip`.

## 🔧 Matériel compatible

- Raspberry Pi Pico W
- Tout microcontrôleur compatible MicroPython et disposant du WiFi

## 📦 Dépendances

- MicroPython récent avec support du module `mip`
- La bibliothèque  [fasapico.py](https://github.com/dfasani/fasapico/blob/main/libs/fasapico.py) contenant la fonction `connect_to_wifi()` 

## 📝 Script Python

```python
import mip
from fasapico import *

# --- Connexion au WiFi ---
# --> Modifier le mot de passe si nécessaire
print("Connexion au réseau WiFi...")
ip = connect_to_wifi(ssid = "icam_iot", password = "Summ3#C@mp2022")

print("\nConnecté ! Adresse IP :", ip)

# --- Installation avec mip ---
print("Installation de micropython-phew avec mip...")
mip.install("github:pimoroni/phew")
print("Installation terminée.")
