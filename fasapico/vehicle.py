from .motors import Moteur

class Voiture:
    def __init__(self, moteur_a, moteur_b, moteur_c, moteur_d):
        """Initialisation de la voiture avec 4 moteurs"""
        self.moteur_a = moteur_a
        self.moteur_b = moteur_b
        self.moteur_c = moteur_c
        self.moteur_d = moteur_d

    def avancer(self):
        self.moteur_a.avant()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.avant()

    def reculer(self):
        self.moteur_a.arriere()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.arriere()

    def glisser_droite(self):
        self.moteur_a.arriere()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.arriere()

    def glisser_gauche(self): 
        self.moteur_a.avant()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.avant()

    def rotation_horaire(self):
        self.moteur_a.avant()
        self.moteur_b.arriere()
        self.moteur_c.avant()
        self.moteur_d.arriere()

    def rotation_anti_horaire(self):
        self.moteur_a.arriere()
        self.moteur_b.avant()
        self.moteur_c.arriere()
        self.moteur_d.avant()

    def diagonale_avant_droite(self):
        self.moteur_a.stop()
        self.moteur_b.avant()
        self.moteur_c.avant()
        self.moteur_d.stop()
        
    def diagonale_arriere_gauche(self):
        self.moteur_a.stop()
        self.moteur_b.arriere()
        self.moteur_c.arriere()
        self.moteur_d.stop()

    def diagonale_avant_gauche(self):
        self.moteur_a.avant()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.avant()

    def diagonale_arriere_droite(self):
        self.moteur_a.arriere()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.arriere()


    def stop(self):
        self.moteur_a.stop()
        self.moteur_b.stop()
        self.moteur_c.stop()
        self.moteur_d.stop()
        
    def definir_vitesse(self, gaz):
        self.moteur_a.definir_vitesse(gaz)
        self.moteur_b.definir_vitesse(gaz)
        self.moteur_c.definir_vitesse(gaz)
        self.moteur_d.definir_vitesse(gaz)

    def definir_vitesse_pourcentage(self, pourcentage):
        """Définit la vitesse de tous les moteurs en pourcentage (0-100)"""
        self.moteur_a.definir_vitesse_pourcentage(pourcentage)
        self.moteur_b.definir_vitesse_pourcentage(pourcentage)
        self.moteur_c.definir_vitesse_pourcentage(pourcentage)
        self.moteur_d.definir_vitesse_pourcentage(pourcentage)

    def piloter_differentiel(self, vitesse, direction):
        """
        Pilote la voiture comme un char (tank drive/différentiel).
        vitesse: de -100 (arrière) à 100 (avant)
        direction: de -100 (gauche) à 100 (droite)
        """
        vg = vitesse + direction
        vd = vitesse - direction
        
        # Normalisation automatique pour rester entre -100 et 100
        max_val = max(abs(vg), abs(vd))
        if max_val > 100:
            vg = (vg / max_val) * 100
            vd = (vd / max_val) * 100

        def _appliquer(moteur, v):
            if v > 0:
                moteur.avant()
                moteur.definir_vitesse_pourcentage(v)
            elif v < 0:
                moteur.arriere()
                moteur.definir_vitesse_pourcentage(abs(v))
            else:
                moteur.stop()

        # Moteurs Gauche (A et C)
        _appliquer(self.moteur_a, vg)
        _appliquer(self.moteur_c, vg)
        # Moteurs Droite (B et D)
        _appliquer(self.moteur_b, vd)
        _appliquer(self.moteur_d, vd)

    def arreter_progressivement(self, pas=500):
        """Réduit la vitesse de tous les moteurs jusqu'à l'arrêt complet."""
        self.moteur_a.arret_progressif(pas)
        self.moteur_b.arret_progressif(pas)
        self.moteur_c.arret_progressif(pas)
        self.moteur_d.arret_progressif(pas)

    def faire_demi_tour(self, duree_ms=1000):
        """Effectue une rotation pour tenter un demi-tour."""
        import time
        self.rotation_horaire()
        time.sleep_ms(duree_ms)
        self.stop()

    def manoeuvre_evitement(self):
        """Petite séquence d'évitement : reculer, tourner, repartir."""
        import time
        self.stop()
        time.sleep_ms(200)
        self.reculer()
        self.definir_vitesse_pourcentage(40)
        time.sleep_ms(500)
        self.rotation_horaire()
        time.sleep_ms(600)
        self.stop()

    def vibrer(self, frequence_ms=50, repetitions=5):
        """Fait vibrer la voiture en alternant rapidement avant/arrière."""
        import time
        for _ in range(repetitions):
            self.avancer()
            self.definir_vitesse_pourcentage(50)
            time.sleep_ms(frequence_ms)
            self.reculer()
            time.sleep_ms(frequence_ms)
        self.stop()

    def piloter_omnidirectionnel(self, direction_deg, puissance):
        """
        Déplacement omnidirectionnel (0-360°).
        0°: Avant, 90°: Droite, 180°: Arrière, 270°: Gauche.
        puissance: 0-100.
        """
        import math
        rad = math.radians(direction_deg)
        # Calcul des composantes pour roues Mecanum
        # Moteurs A(FL), B(FR), C(RL), D(RR)
        # Formule simplifiée pour Mecanum
        sin_val = math.sin(rad + math.pi/4)
        cos_val = math.cos(rad + math.pi/4)
        
        va = sin_val * puissance
        vb = cos_val * puissance
        vc = cos_val * puissance
        vd = sin_val * puissance

        def _appliquer(moteur, v):
            if v > 0:
                moteur.avant()
                moteur.definir_vitesse_pourcentage(abs(v))
            elif v < 0:
                moteur.arriere()
                moteur.definir_vitesse_pourcentage(abs(v))
            else:
                moteur.stop()

        _appliquer(self.moteur_a, va)
        _appliquer(self.moteur_b, vb)
        _appliquer(self.moteur_c, vc)
        _appliquer(self.moteur_d, vd)

    def carre(self, cote_ms=1000):
        """Parcours un carré en utilisant les glissements latéraux."""
        import time
        self.definir_vitesse_pourcentage(50)
        self.avancer()
        time.sleep_ms(cote_ms)
        self.glisser_droite()
        time.sleep_ms(cote_ms)
        self.reculer()
        time.sleep_ms(cote_ms)
        self.glisser_gauche()
        time.sleep_ms(cote_ms)
        self.stop()

    def zigzag(self, pas_ms=500, iterations=3):
        """Avance en zigzaguant."""
        import time
        self.definir_vitesse_pourcentage(60)
        for _ in range(iterations):
            self.diagonale_avant_droite()
            time.sleep_ms(pas_ms)
            self.diagonale_avant_gauche()
            time.sleep_ms(pas_ms)
        self.stop()

    def demonstration(self):
        """Séquence de démonstration des capacités mecanum."""
        import time
        self.vibrer()
        time.sleep_ms(500)
        self.glisser_droite()
        self.definir_vitesse_pourcentage(50)
        time.sleep_ms(1000)
        self.glisser_gauche()
        time.sleep_ms(1000)
        self.rotation_horaire()
        time.sleep_ms(1000)
        self.stop()
