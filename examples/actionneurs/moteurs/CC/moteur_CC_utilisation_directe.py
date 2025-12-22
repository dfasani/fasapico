from machine import Pin, PWM
import time

# 1. CONFIGURATION (Le "Setup")
# On définit les broches de direction comme des sorties simples
in1 = Pin(11, Pin.OUT)
in2 = Pin(12, Pin.OUT)

# On définit la broche de vitesse (ENA) comme une sortie PWM
ena = PWM(Pin(13) , freq=1000)  # Fréquence de 1 kHz

print("--- MODE MANUEL SANS CLASSE ---")

# --- MARCHE AVANT ---
print("Action : Marche avant")
in1.value(0)       # IN1 à l'état BAS
in2.value(1)       # IN2 à l'état HAUT
ena.duty_u16(40000) # Vitesse environ 60%
time.sleep(2)

# --- CHANGEMENT DE DIRECTION ---
print("Action : Marche arrière a fond")
in1.value(1)       # On inverse les états
in2.value(0)       # IN1 haut, IN2 bas
ena.duty_u16(65535)
time.sleep(2)

# --- ARRÊT ---
print("Action : Stop")
in1.value(0)       # Tout à zéro
in2.value(0)
ena.duty_u16(0)    # Plus de puissance
