from machine import Pin, PWM
import time
from .utils import scale, scale_to_int

class Moteur:
    def __init__(self, broche_in1, broche_in2, broche_pwm, vitesse=0):
        """
        Initialise le moteur avec les broches spécifiées et une vitesse initiale a 0 par defaut.
        """
        if not all(isinstance(b, int) and 0 <= b <= 27 for b in [broche_in1, broche_in2, broche_pwm]):
            raise ValueError("Les broches doivent être des entiers valides pour la plateforme.")
        
        self.in1 = Pin(broche_in1, Pin.OUT)
        self.in2 = Pin(broche_in2, Pin.OUT)
        self.pwm = PWM(Pin(broche_pwm), freq=1000, duty_u16=0)
        self.etat = "arrêté"  # "avant", "arrière", ou "arrêté"
        self.definir_vitesse(vitesse)

    def definir_vitesse(self, gaz):
        """
        Définit la vitesse (0 à 65535).
        Si la vitesse est un float, elle est convertie en int.
        Lève une exception si la valeur est hors limites.
        """
        if isinstance(gaz, float):
            gaz = int(gaz)
        if not (0 <= gaz <= 65535):
            raise ValueError("La vitesse doit être un entier entre 0 et 65535.")
        self.pwm.duty_u16(gaz)

    def definir_vitesse_pourcentage(self, pourcentage):
        """
        Définit la vitesse en pourcentage (0 à 100).
        """
        if not (0 <= pourcentage <= 100):
            raise ValueError("Le pourcentage doit être entre 0 et 100.")
        gaz = scale_to_int(pourcentage, 0, 100, 0, 65535)
        self.definir_vitesse(gaz)

    def avant(self):
        """Active la rotation en avant."""
        self.in1.low()
        self.in2.high()
        self.etat = "avant"

    def arriere(self):
        """Active la rotation en arrière."""
        self.in1.high()
        self.in2.low()
        self.etat = "arrière"

    def stop(self):
        """Arrête le moteur (roue libre)."""
        self.in1.low()
        self.in2.low()
        self.etat = "stop"

    def freiner(self):
        """Freinage actif (court-circuitage du moteur)."""
        self.in1.high()
        self.in2.high()
        self.pwm.duty_u16(65535)
        self.etat = "freinage"

    def set_direction_et_vitesse(self, direction, vitesse):
        """
        Définit la direction ('avant' ou 'arriere') et la vitesse.
        """
        if direction == "avant":
            self.avant()
        elif direction == "arriere":
            self.arriere()
        else:
            raise ValueError("La direction doit être 'avant' ou 'arrière'.")
        self.definir_vitesse(vitesse)

    def arret_progressif(self, pas=500):
        """
        Réduit progressivement la vitesse jusqu'à 0 avant d'arrêter le moteur.
        """
        vitesse_actuelle = self.pwm.duty_u16()
        for v in range(vitesse_actuelle, -1, -pas):
            self.definir_vitesse(max(0, v))
            time.sleep(0.05)  # Pause pour donner le temps au moteur de ralentir
        self.definir_vitesse(0)
        self.stop()

    def get_etat(self):
        """
        Retourne l'état actuel du moteur.
        """
        return {
            "direction": self.etat,
            "vitesse": self.pwm.duty_u16()
        }
    
    def __str__(self):
        # Retourne une chaîne de caractères contenant l'état du moteur
        return f"Moteur({self.in1}, {self.in2}, {self.pwm}, Etat: {self.etat}, PWM: {self.pwm.duty_u16()})"

class Stepper:
    def __init__(self, pin1=10, pin2=11, pin3=12, pin4=13, steps_per_rev=2048):
        self.pins = [Pin(pin1, Pin.OUT), Pin(pin2, Pin.OUT), Pin(pin3, Pin.OUT), Pin(pin4, Pin.OUT)]
        self.steps_per_rev = steps_per_rev
        self.delay_ms = 5

    def set_speed_rpm(self, rpm):
        """Définit la vitesse en tours par minute."""
        if rpm > 0:
            # Calcul approximatif du délai entre chaque pas
            self.delay_ms = max(2, int(60000 / (rpm * self.steps_per_rev / 4)))

    def move(self, nbPas):
        if nbPas > 0:
            steps_sequence = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        else:
            steps_sequence = [[0,0,0,1], [0,0,1,0], [0,1,0,0], [1,0,0,0]]
            
        for _ in range(abs(nbPas)):
            for step in steps_sequence:
                for i in range(4):
                    self.pins[i].value(step[i])
                time.sleep_ms(self.delay_ms)

    def move_to_angle(self, angle_deg):
        """Déplace le moteur jusqu'à un angle donné (relatif)."""
        nb_pas = int((angle_deg / 360) * self.steps_per_rev)
        self.move(nb_pas)
