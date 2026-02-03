# -*- coding:utf-8 -*-
from fasapico import *
from fasapico.motors import ServoMoteur
from machine import Pin, ADC
import time

# --- CONFIGURATION ---
PIN_ADC = 27
PINS_STEPPER = [10, 11, 12, 13]
PIN_SERVO = 7

def test_maquette_globale():
    print("--- DÉMARRAGE DU TEST GLOBAL ---")

    # 1. TEST LCD & BOUSSOLE
    print("1/5 - Initialisation LCD et Boussole...")
    lcd = Grove_LCD_I2C()
    boussole = Boussole()
    
    lcd.clear()
    lcd.write("Test en cours...")
    
    if boussole.sensor_init() != boussole.ERROR:
        cap = boussole.get_compass_degree()
        msg = f"Cap: {cap:.0f} deg"
        print(f"[OK] Boussole : {msg}")
        lcd.clear()
        lcd.write(msg)
    else:
        print("[ERR] Boussole non detectee")
    time.sleep(2)

    # 2. TEST ADC (Capteur analogique)
    print("2/5 - Lecture ADC...")
    adc = ADC(PIN_ADC)
    valeur = adc.read_u16()
    print(f"[OK] Valeur ADC : {valeur}")
    lcd.clear()
    lcd.write(f"ADC: {valeur}")
    time.sleep(2)

    # 3. TEST SERVO (Mouvement rapide)
    print("3/5 - Test Servo...")
    servo = ServoMoteur(PIN_SERVO, angle_min=50, angle_max=130)
    servo.min()
    time.sleep(0.5)
    servo.max()
    time.sleep(0.5)
    servo.centre()
    servo.desactiver()
    print("[OK] Servo testé")

    # 4. TEST MOTEUR PAS-À-PAS (Une rotation courte)
    print("4/5 - Test Moteur Pas-a-Pas...")
    stepper_pins = [Pin(p, Pin.OUT) for p in PINS_STEPPER]
    seq = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
    
    for _ in range(20): # Petit mouvement
        for step in seq:
            for i in range(4):
                stepper_pins[i].value(step[i])
            time.sleep_ms(10)
    print("[OK] Moteur PAP testé")

    # 5. FIN
    print("5/5 - Fin du test")
    lcd.clear()
    lcd.write("TEST TERMINE\nTOUT EST OK")
    print("--- TEST TERMINE AVEC SUCCÈS ---")

if __name__ == "__main__":
    test_maquette_globale()
