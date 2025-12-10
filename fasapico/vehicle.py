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
