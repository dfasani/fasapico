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


class ServoMoteur:
    """
    Classe pour contrôler un servo moteur standard (SG90, MG90S, etc.).
    
    Les servos standards utilisent un signal PWM à 50Hz avec un duty cycle
    variant entre ~2.5% (0°) et ~12.5% (180°).
    """
    
    def __init__(self, broche, angle_min=0, angle_max=180, freq=50, 
                 duty_min=1638, duty_max=8192):
        """
        Initialise le servo moteur.
        
        Args:
            broche: Numéro de la broche GPIO
            angle_min: Angle minimum (par défaut 0°)
            angle_max: Angle maximum (par défaut 180°)
            freq: Fréquence PWM en Hz (par défaut 50Hz pour les servos standards)
            duty_min: Duty cycle minimum (0°) en u16 (par défaut ~2.5% = 1638)
            duty_max: Duty cycle maximum (180°) en u16 (par défaut ~12.5% = 8192)
        """
        if not isinstance(broche, int) or not (0 <= broche <= 27):
            raise ValueError("La broche doit être un entier valide (0-27).")
        
        self.pwm = PWM(Pin(broche), freq=freq, duty_u16=0)
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.duty_min = duty_min
        self.duty_max = duty_max
        self._angle_actuel = None
    
    def definir_angle(self, angle):
        """
        Définit l'angle du servo moteur.
        
        Args:
            angle: Angle souhaité (entre angle_min et angle_max)
        """
        if not (self.angle_min <= angle <= self.angle_max):
            raise ValueError(f"L'angle doit être entre {self.angle_min} et {self.angle_max}.")
        
        duty = scale_to_int(angle, self.angle_min, self.angle_max, 
                           self.duty_min, self.duty_max)
        self.pwm.duty_u16(duty)
        self._angle_actuel = angle
    
    def definir_pourcentage(self, pourcentage):
        """
        Définit la position du servo en pourcentage (0% = angle_min, 100% = angle_max).
        
        Args:
            pourcentage: Position en pourcentage (0 à 100)
        """
        if not (0 <= pourcentage <= 100):
            raise ValueError("Le pourcentage doit être entre 0 et 100.")
        
        angle = scale(pourcentage, 0, 100, self.angle_min, self.angle_max)
        self.definir_angle(angle)
    
    def centre(self):
        """Place le servo à sa position centrale (90° par défaut)."""
        angle_centre = (self.angle_min + self.angle_max) / 2
        self.definir_angle(angle_centre)
    
    def min(self):
        """Place le servo à sa position minimale."""
        self.definir_angle(self.angle_min)
    
    def max(self):
        """Place le servo à sa position maximale."""
        self.definir_angle(self.angle_max)
    
    def desactiver(self):
        """Désactive le signal PWM (le servo ne maintient plus sa position)."""
        self.pwm.duty_u16(0)
    
    def balayage(self, pas=5, delai_ms=50):
        """
        Effectue un balayage de l'angle minimum à l'angle maximum.
        
        Args:
            pas: Incrément d'angle par étape (par défaut 5°)
            delai_ms: Délai entre chaque étape en ms (par défaut 50ms)
        """
        for angle in range(self.angle_min, self.angle_max + 1, pas):
            self.definir_angle(angle)
            time.sleep_ms(delai_ms)
        for angle in range(self.angle_max, self.angle_min - 1, -pas):
            self.definir_angle(angle)
            time.sleep_ms(delai_ms)
    
    def get_angle(self):
        """Retourne l'angle actuel du servo."""
        return self._angle_actuel
    
    def __str__(self):
        return f"ServoMoteur(angle={self._angle_actuel}, min={self.angle_min}, max={self.angle_max})"
