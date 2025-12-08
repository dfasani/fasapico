#
# Etape 1 : Connection au reseau WiFi
#

from fasapico import *

#
# Etape 1 : Connection au reseau WiFi
#

ip = connect_to_wifi()


#
# Etape 2 : Requete vers le serveur
#

import urequests
r = urequests.get("http://google.fr")
print(r.content) #affiche le corps de la reponse

r.close() # <-- ULTRA IMPORTANT : FERMER LA REQUETE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
