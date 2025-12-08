import pyglet
import paho.mqtt.client as mqtt

# Configuration
broker = "mqtt.dev.icam.school"
port = 1883
topic = "bzh/iot/bateau/monBateau/"  # Make sure this matches your boat's subscription

client = mqtt.Client()
client.connect(broker, port)

pyglet.app.platform_event_loop.start()
joysticks = pyglet.input.get_joysticks()

if not joysticks:
    print("No joystick found.")

for joystick in joysticks:
    joystick.open()
    print(f"Joystick detected: {joystick.device}")

    @joystick.event
    def on_joybutton_press(joystick , button ):
        msg = f"{topic}bouton|{button}"
        print(f"Sending: {msg}")
        # Note: the boat expects specific topics, logic might need adjustment 
        # based on what the boat subscribes to.
        # But per request, we standardize the prefix.
        client.publish(topic + "bouton", str(button)) # Example adaptation

    @joystick.event
    def on_joyaxis_motion(joystick , axis, value):
        # Determine topic suffix based on axis for clearer control
        subtopic = "axis"
        msg = f"{axis}|{value}"
        print(f"Sending to {topic}{subtopic}: {msg}")
        client.publish(topic + subtopic, msg)

pyglet.app.run()
