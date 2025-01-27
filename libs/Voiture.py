
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
        """
        Définit la vitesse (0 à 65535).
        Si la vitesse est un float, elle est convertie en int.
        Lève une exception si la valeur est hors limites.
        """
        self.moteur_a.definir_vitesse(gaz)
        self.moteur_b.definir_vitesse(gaz)
        self.moteur_c.definir_vitesse(gaz)
        self.moteur_d.definir_vitesse(gaz)

    
    def differentiel(self, traingauche, traindroit):
        
        """
        Permet de régler la vitesse des moteurs gauche (A et C) et droit (B et D) pour un contrôle différentiel.
        Les vitesses doivent être comprises entre -100 et 100.

        - traingauche : vitesse des moteurs A et C (-100 à 100)
        - traindroit  : vitesse des moteurs B et D (-100 à 100)
        """

        # Vérifier si les vitesses sont bien dans la plage acceptable
        if not (-100 <= traingauche <= 100):
            raise ValueError("La vitesse de traingauche doit être comprise entre -100 et 100.")
        if not (-100 <= traindroit <= 100):
            raise ValueError("La vitesse de traindroit doit être comprise entre -100 et 100.")

        # Convertir les vitesses de -100 à 100 vers la plage 0 à 65535 pour le PWM
        vitesse_gauche = scale_to_int(abs(traingauche), 0, 100, 0, 65535)
        vitesse_droite = scale_to_int(abs(traindroit), 0, 100, 0, 65535)
        
        self.moteur_a.definir_vitesse(vitesse_gauche)
        self.moteur_c.definir_vitesse(vitesse_gauche)
        self.moteur_b.definir_vitesse(vitesse_droite)
        self.moteur_d.definir_vitesse(vitesse_droite)
        
        # Gestion des moteurs gauche (A et C)
        if traingauche > 0:
            # Les moteurs A et C vont en avant
            self.moteur_a.avant()
            self.moteur_c.avant()         
        else:
            # Les moteurs A et C vont en arrière
            self.moteur_a.arriere()
            self.moteur_c.arriere()


        # Gestion des moteurs droit (B et D)
        if traindroit > 0:
            # Les moteurs B et D vont en avant
            self.moteur_b.avant()
            self.moteur_d.avant()
        else:
            # Les moteurs B et D vont en arrière
            self.moteur_b.arriere()
            self.moteur_d.arriere()
          
