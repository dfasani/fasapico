# -*- coding:utf-8 -*-
from fasapico import *
from fasapico.motors import ServoMoteur
from machine import Pin, ADC
import time
import sys
import uselect

# --- CONFIGURATION ---
PIN_ADC = 27
PINS_STEPPER = [10, 11, 12, 13]
PIN_SERVO = 7

# On prépare le "lecteur" de clavier non-bloquant
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def a_appuye_entree():
    """Vérifie si la touche Entrée a été pressée sans bloquer le code."""
    return bool(spoll.poll(0))

def vider_buffer():
    """Vide les caractères restants dans le tampon d'entrée."""
    while spoll.poll(0):
        sys.stdin.read(1)

def boucle_jusque_entree(nom, action_unitaire):
    """Exécute 'action_unitaire' en boucle jusqu'à un appui sur Entrée."""
    print(f"\n>>> TEST EN COURS : {nom}")
    print(">>> Appuyez sur [ENTREE] pour passer au test suivant.")
    
    vider_buffer() # On ignore les appuis accidentels précédents
    
    while True:
        action_unitaire()
        if a_appuye_entree():
            print(f"[FIN DU TEST : {nom}]")
            break

# --- ACTIONS UNITAIRES ---

def action_boussole(boussole, lcd):
    if boussole.sensor_init() != boussole.ERROR:
        cap = boussole.get_compass_degree()
        msg = f"Cap: {cap:.1f} deg"
        print(msg)
        lcd.clear()
        lcd.write(msg)
    time.sleep(0.5)

def action_adc(adc, lcd):
    valeur = adc.read_u16()
    print(f"ADC: {valeur}")
    lcd.clear()
    lcd.write(f"Potar: {valeur}")
    time.sleep(0.1)

def action_servo(servo):
    servo.min()
    time.sleep(0.6)
    servo.max()
    time.sleep(0.6)

def action_stepper(stepper_pins, seq):
    for step in seq:
        for i in range(4):
            stepper_pins[i].value(step[i])
        time.sleep_ms(10)

# --- PROGRAMME PRINCIPAL ---

def main():
    # Initialisations
    lcd = Grove_LCD_I2C()
    boussole = Boussole()
    adc = ADC(PIN_ADC)
    servo = ServoMoteur(PIN_SERVO, angle_min=50, angle_max=130)
    stepper_pins = [Pin(p, Pin.OUT) for p in PINS_STEPPER]
    seq = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]

    # Lancement des boucles
    boucle_jusque_entree("BOUSSOLE", lambda: action_boussole(boussole, lcd))
    boucle_jusque_entree("POTENTIOMETRE", lambda: action_adc(adc, lcd))
    boucle_jusque_entree("SERVO", lambda: action_servo(servo))
    boucle_jusque_entree("MOTEUR PAS-A-PAS", lambda: action_stepper(stepper_pins, seq))

    # Nettoyage
    for pin in stepper_pins: pin.value(0)
    servo.desactiver()
    print("\n--- TOUS LES TESTS SONT TERMINÉS ---")

if __name__ == "__main__":
    main()
