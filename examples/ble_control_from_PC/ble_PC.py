import asyncio
from bleak import *

# Adresse du robot Pico (par exemple)
PICO_NAME = "schumi"

# Constantes pour les UUIDs du service UART
UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"

# Fonction de connexion et d'envoi de commande
async def control_robot():
    # Scan et connexion au robot
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == PICO_NAME:
            async with BleakClient(device) as client:
                print(f"Connected to {device.name}")

                # Envoyer des commandes
                await client.write_gatt_char(UART_RX_UUID, b'forward')  # Exemple de commande 'forward'
                await asyncio.sleep(1)
                await client.write_gatt_char(UART_RX_UUID, b'stop')     # Commande pour stopper

# Démarrage de la boucle asyncio
asyncio.run(control_robot())

