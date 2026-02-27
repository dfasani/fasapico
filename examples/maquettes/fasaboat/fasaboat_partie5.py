from fasapico import *
from time import *

compasNumerique = Boussole()

#on va utiliser le CAN de la broche 27
adc = machine.ADC(27)

#on utilise la resistance interne de PULL UP pour les BP
button20 = Pin(20, Pin.IN, Pin.PULL_UP)
button21 = Pin(21, Pin.IN, Pin.PULL_UP)
button22 = Pin(22, Pin.IN, Pin.PULL_UP)

# pour rappel voici le fonctionnement du servo
# https://github.com/dfasani/fasapico/blob/main/examples/actionneurs/moteurs/servo/servomoteur.py
servo = PWM(Pin(7) , freq=50)

SERVO_BABORD  = 3000 #valeur min pour aller à babord toutes
SERVO_CENTRE  = 5000 #valeur pour barre au centre
SERVO_TRIBORD = 7000 #valeur min pour aller à tribord toutes

pins = [
        Pin(10,Pin.OUT),
        Pin(11,Pin.OUT),
        Pin(12,Pin.OUT),
        Pin(13,Pin.OUT)
    ]


#fonction qui fait tourner le moteur pas a pas dans un sens ou dans l'autre
def runStepper(nbDegres):
    nbDegres = nbDegres * 1.33 #petite correction necessaire pour aller a 90°
    if nbDegres > 0 :
        steps_sequence = [     
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ]
        
    else:
        steps_sequence = [     
            [0,0,0,1],
            [0,0,1,0],
            [0,1,0,0],
            [1,0,0,0]
        ]
        
    
    for _ in range(abs(nbDegres)):
        for step in steps_sequence:         # pour chacune des etapes
                for i in range(4):          # pour chacune des 4 broches (i de 0 à 3)
                    pins[i].value(step[i])  # maj PIN n° i
                sleep_ms(10)                 # il faut attendre un peu pour laisser le temps au moteur de deplacer
    




print("Positionne la voile à l'origine stp")
for i in range(4):   # i de 0 à 3
    pins[i].value(0) # maj PIN n° i
sleep_ms(5000)
print("C'est parti !")


positionVoileActuelle = 0
piloteAutoActive = False #par defaut le pilote automatique est desactive

while True:
    
    #attente entre deux tours (ça suffit amplement)
    sleep_ms(10)
    
    
    #si BP 20 presse
    if button20.value() == 0 :  
        print("maj cap manuelle, desactivation pilote auto")
        piloteAutoActive = False
        
        #
        #completer ici pour la question 5a
        #
        
        #1 - lecture potar
        #potValeur = adc ...
        
        #2 - conversion
        #potValeur est dans [0;65535] il faut le ramener dans [SERVO_BABORD ; SERVO_TRIBORD] soit [3000 ; 7000]
        # La fonction scale_to_int() est super pratique ici !
        #rapportCyclique = scale_to_int(....     # importer fasapico en début de fichier, la doc est ici --> https://github.com/dfasani/fasapico/blob/main/examples/use_scale_function.py
        
        #3 - signal PWM pour servo
        #generer un signal PWM a destination du servo (c.f. exemple https://github.com/dfasani/fasapico/blob/main/examples/actionneurs/moteurs/servo/servomoteur.py)
        
        
    
    #si BP 21 presse
    if button21.value() == 0 :
        print("maj voile")
        
        
        #
        #completer ici pour la question 5b
        #
        
        #1 - lecture potar
        #potValeur = ...
        
        #2 - conversion
        #la position demandee est calculee en fonction de la valeur du pot
        #positionVoileDemandee = int(scale(potValeur,0,65535, -90 , 90 ))   
        
        #3 - calcul du mouvement
        #on calcule le deplacement a realiser : positionVoileActuelle - positionVoileDemandee
        #cette difference nous donne un certain nombre de pas , positif ou negatif
        #deplacementVoile =
        
        #print("potValeur : " , potValeur , "positionVoileActuelle : " , positionVoileActuelle , "positionVoileDemandee : " , positionVoileDemandee , "deplacementVoile : " , deplacementVoile) , 
        
        # 4 - deplacement
        #appel a runStepper() en lui indiquant le deplacement a realiser
        #runStepper(deplacementVoile)
        
        #5 - maj position
        #maj positionVoileActuelle =  positionVoileDemandee car on a fait le deplacement
        #positionVoileActuelle = ...
                    
    #si BP 22 presse
    if button22.value() == 0 :
        print("pilote automatique active")
        piloteAutoActive = True
     
     
     
    #
    #completer ici pour la question 5c
    #   
    
    #if piloteAutoActive :
        
        #suivez le guide ! https://docs.google.com/presentation/d/11LwDaPO2U39pykqkscvoBE46eYIiO89CcwuR1NeAp1c/edit#slide=id.g2bacf4f14c9_0_111
        
        
        #1 -lecture boussole pour maj cap
            
        # comme dans la partie precedente, on corrige le cap 
        
        
        #2 - calcul du rapport cyclique

        #zone 1
        #if lectureCap > 270 :
            #print("bateau dans la zone 1 : BABORD TOUTES")
            #commandeServo = ...
        #    ....
        
        #zone 2
        #elif lectureCap < 90 :
            #print("bateau dans la zone 2 : TRIBORD TOUTES")
            #    ...
            # tribord toutes
            #commandeServo = ...
            
        #zone 3
        #else :
            #print("bateau dans la zone 3")
            #maj proportionnelle du gouvernail avec la fonction scale
            # 180 --> barre au centre
            # 270 --> babord toutes
            # 190 --> tres léger babord
            # 255 --> fort babord
            # 90 --> tribord toutes
            # 100 --> léger tribord
            # 170 --> tres léger tribord
            #commandeServo = ...
      
        
        #3 afficher valeur de la boussole et commandeServo
        #print()
            
        #3 - transmission de la valeur de commandeServo au safran (signal PWM pour servo entre 3000 et 7000)

        #servo.duty ...  (commandeServo)

