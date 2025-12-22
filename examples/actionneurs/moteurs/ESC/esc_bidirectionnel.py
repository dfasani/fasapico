from machine import *
from time import *

# Déclarer la broche pour le signal PWM
# Fréquence fixe de 50 Hz pour l'ESC
pwm_output = PWM(Pin(0) , freq=50)

def set_pwm(duty_percent):
    """
    Définit le signal PWM correspondant au pourcentage de vitesse (-100% à 100%).
    """
    # Convertir le pourcentage en largeur d'impulsion (1 ms à 2 ms)
    min_pulse = 1070  		# ~1   ms en microsecondes
    max_pulse = 1852  		# ~2   ms en microsecondes
    neutral_pulse = 1488  	# ~1.5 ms pour l'arrêt (neutre)

    if duty_percent < -100 or duty_percent > 100:
        print("Pourcentage invalide. Doit être entre -100 et 100.")
        return

    pulse = int(neutral_pulse + (duty_percent / 100) * (max_pulse - min_pulse) / 2)
    duty_u16 = int(pulse / 20000 * 65535)  # Convertir en valeur 16 bits pour duty_u16
    pwm_output.duty_u16(duty_u16)
    print(f"Duty Percent: {duty_percent} -> Pulse Width: {pulse} µs")

#initialisation à 0 (petits bips attendus de la part de l'ESC)
set_pwm(0)

while True:
    try:
        duty_cycle = float(input("Entrez la vitesse (-100 à 100) : "))
        set_pwm(duty_cycle)
    except ValueError:
        print("Veuillez entrer un nombre valide.")
    sleep(0.1)

