"""
Programme de test pour la classe ServoMoteur.
Teste toutes les fonctionnalités du servo moteur sur une broche GPIO.
"""

from fasapico.motors import ServoMoteur
import time

# Configuration - Modifier selon votre branchement
BROCHE_SERVO = 7  # Broche GPIO du servo

# Limites d'angle pour éviter les butées mécaniques
ANGLE_MIN = 50
ANGLE_MAX = 130
DUTY_MIN = 3000
DUTY_MAX = 7000

def test_angles():
    """Test des positions angulaires."""
    print("=== Test des angles ===")
    servo = ServoMoteur(BROCHE_SERVO, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX, 
                        duty_min=DUTY_MIN, duty_max=DUTY_MAX)
    
    # Test position minimum
    print(f"Position minimum ({ANGLE_MIN}°)")
    servo.min()
    time.sleep(1)
    
    # Test position centrale
    print(f"Position centrale ({(ANGLE_MIN + ANGLE_MAX) // 2}°)")
    servo.centre()
    time.sleep(1)
    
    # Test position maximum
    print(f"Position maximum ({ANGLE_MAX}°)")
    servo.max()
    time.sleep(1)
    
    # Retour au centre
    servo.centre()
    servo.desactiver()
    print("Test angles terminé\n")

def test_angles_specifiques():
    """Test de positions angulaires spécifiques."""
    print("=== Test angles spécifiques ===")
    servo = ServoMoteur(BROCHE_SERVO, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX,
                        duty_min=DUTY_MIN, duty_max=DUTY_MAX)
    
    angles = [ANGLE_MIN, 60, 90, 120, ANGLE_MAX]
    for angle in angles:
        print(f"Angle: {angle}°")
        servo.definir_angle(angle)
        time.sleep(0.5)
    
    servo.desactiver()
    print("Test angles spécifiques terminé\n")

def test_pourcentage():
    """Test du contrôle par pourcentage."""
    print("=== Test pourcentage ===")
    servo = ServoMoteur(BROCHE_SERVO, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX,
                        duty_min=DUTY_MIN, duty_max=DUTY_MAX)
    
    pourcentages = [0, 25, 50, 75, 100]
    for pct in pourcentages:
        print(f"Position: {pct}%")
        servo.definir_pourcentage(pct)
        time.sleep(0.5)
    
    servo.desactiver()
    print("Test pourcentage terminé\n")

def test_balayage():
    """Test du balayage automatique."""
    print("=== Test balayage ===")
    servo = ServoMoteur(BROCHE_SERVO, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX,
                        duty_min=DUTY_MIN, duty_max=DUTY_MAX)
    
    print("Balayage lent (pas=10, delai=100ms)")
    servo.balayage(pas=10, delai_ms=100)
    
    print("Balayage rapide (pas=5, delai=30ms)")
    servo.balayage(pas=5, delai_ms=30)
    
    servo.centre()
    servo.desactiver()
    print("Test balayage terminé\n")

def test_servo_custom():
    """Test avec paramètres personnalisés."""
    print("=== Test servo custom (70-110°) ===")
    # Servo limité à un débattement spécifique à l'intérieur de la plage de sécurité
    servo = ServoMoteur(BROCHE_SERVO, angle_min=70, angle_max=110)
    
    print("Min (70°)")
    servo.min()
    time.sleep(0.5)
    
    print("Centre (90°)")
    servo.centre()
    time.sleep(0.5)
    
    print("Max (110°)")
    servo.max()
    time.sleep(0.5)
    
    servo.desactiver()
    print("Test servo custom terminé\n")

def test_info():
    """Test de l'affichage d'informations."""
    print("=== Test informations ===")
    servo = ServoMoteur(BROCHE_SERVO, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX,
                        duty_min=DUTY_MIN, duty_max=DUTY_MAX)
    
    servo.definir_angle(60)
    print(f"Servo: {servo}")
    print(f"Angle actuel: {servo.get_angle()}°")
    
    servo.definir_angle(120)
    print(f"Servo: {servo}")
    print(f"Angle actuel: {servo.get_angle()}°")
    
    servo.desactiver()
    print("Test informations terminé\n")

def run_all_tests():
    """Exécute tous les tests."""
    print("=" * 40)
    print("TESTS DE LA CLASSE ServoMoteur")
    print("=" * 40)
    print(f"Broche utilisée: GP{BROCHE_SERVO}\n")
    
    test_angles()
    time.sleep(1)
    
    test_angles_specifiques()
    time.sleep(1)
    
    test_pourcentage()
    time.sleep(1)
    
    test_balayage()
    time.sleep(1)
    
    test_servo_custom()
    time.sleep(1)
    
    test_info()
    
    print("=" * 40)
    print("TOUS LES TESTS TERMINÉS")
    print("=" * 40)

# Exécution principale
if __name__ == "__main__":
    run_all_tests()
