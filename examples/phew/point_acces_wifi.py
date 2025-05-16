from phew import server, access_point , get_ip_address
from time import *

# Démarre un point d'acces WiFi
pointAccesWifi = access_point(ssid = "monBateau", password=None)  # nom du réseau et mot de passe
print("Point d'acces démarré")
print("Adresse IP :", pointAccesWifi.ifconfig()[0])

# Route /servo : récupere un parametre 'angle'
@server.route("/servo", methods=["GET"])
def handle_servo(request):
    angle = request.query.get("angle", None)
    if angle:
        print("Parametre angle recu :", angle)
        
        #faire qqchose ici : eg transmettre l'angle recu au servo
        
        return f"Angle recu : {angle}"
    
    else:
        return "Parametre 'angle' manquant", 400

# Route /vitesse : récupere un parametre 'val'
@server.route("/vitesse", methods=["GET"])
def handle_vitesse(request):
    val = request.query.get("val", None)
    if val:
        print("Parametre vitesse recu :", val)
        
        #faire qqchose ici : eg transmettre le parametre recu au systeme de propulsion

        
        return f"Vitesse recue : {val}"
    else:
        return "Parametre 'val' manquant", 400

# Catch-all pour toute autre route
@server.catchall()
def catchall(request):
    return "Route non trouvee :-(", 404

# Lance le serveur HTTP
server.run()
