from fasapico import *

#
# 1. Je me connecte au WiFi
#
ip = connect_to_wifi(ssid="icam_iot", password = "Summ3#C@mp2022")

#
# 2. J'envoie une requete
#
jsonData = get_json_from_url(url = "https://data.economie.gouv.fr/api/v2/catalog/datasets/controle_techn/facets?refine=code_postal:44210")

#
# 3. J'explore le résultat
#

#tout afficher
#print(jsonData) 

#la 4eme facette (numero 3) c'est la denomination (nom de l'établissement)
cct_denominations = jsonData["facets"][3] 

#je recupete les etablissements de CT
etablissements = cct_denominations["facets"]

#parcours de la liste
for unEtablissement in etablissements :
    print(unEtablissement["name"])
