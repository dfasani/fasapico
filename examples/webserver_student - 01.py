from phew import server, connect_to_wifi

WIFI_SSID = "Icam_IOT"
WIFI_PASSWORD = "V@nn3s2026"

ip = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
print("Received IP adress",ip)

# basic response
@server.route("/hello")
def hello(request):
    return "Salut toi =)"

    # si tu es chaud, tu écrit en HTML !
    #return '<h1>Bonjour</h1><p>Bienvenue dans ton cours</p><img src="http://bit.ly/fasaniot">'

# start the webserver
server.run()
print(server)