from phew import server, connect_to_wifi

WIFI_SSID = "icam_iot"
WIFI_PASSWORD = "Summ3#C@mp2022"

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