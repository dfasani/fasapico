from fasapico import *

# Connect to WiFi using credentials from secrets.py or default
ip = connect_to_wifi()

print('Connected!')
print('IP = ' + ip)

# Robustness check loop example (though connect_to_wifi already handles retries)
wlan = network.WLAN(network.STA_IF)
if wlan.isconnected():
    print("Connection verified.")
else:
    print("Connection lost.")
