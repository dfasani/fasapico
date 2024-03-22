import pyglet
import paho.mqtt.client as mqtt


client = mqtt.Client()
client.connect("broker.hivemq.com", 1883)

topic = "maquette/davidfasani"

pyglet.app.platform_event_loop.start()
joysticks = pyglet.input.get_joysticks()

for joystick in joysticks:
    joystick.open()

    @joystick.event
    def on_joybutton_press(joystick , button ):
        msg = "bouton|"+str(button)
        print(msg)
        client.publish(topic, msg)

    @joystick.event
    def on_joyaxis_motion(joystick , axis, value):
        msg = "axis|"+axis+"|"+str(value)
        print(msg)
        client.publish(topic, msg)

pyglet.app.run()


