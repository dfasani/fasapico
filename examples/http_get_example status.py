#
# Connection au reseau WiFi
#

from fasapico import *

#
# Connection au reseau WiFi
#

ip = connect_to_wifi()


#
# Faire une requete
#

import urequests
r = urequests.get("http://icam.fr")
print(r.status_code) #affiche le statut de la reponse

r = urequests.get("http://icam.fr/laPageQuiNexistePas")
print(r.status_code) #affiche le statut de la reponse



r.close() # <-- ULTRA IMPORTANT : FERMER LA REPONSE SINON ON SE FAIT JETER PAR SERVEUR A LA SUIVANTE !!!
