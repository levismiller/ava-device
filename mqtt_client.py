import paho.mqtt.client as mqtt
import json


class MQTTClient(object):

    def __init__(self, username, passwd, host, client_id, update_ws_clients, port=1883):
        print(type(update_ws_clients))
        self.client_id = client_id
        self.update_ws_clients = update_ws_clients
        self.client = mqtt.Client()
        self.username = username
        self.passwd = passwd
        self.host = host
        self.port = port
        self.register_topic = "device/register"
        self.event_topic = "device/event"
        self.ignored = [self.register_topic]

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {str(rc)}")
        self.client.subscribe("#")

    def send(self, topic, msg):
        self.client.publish(topic, msg)

    def on_message(self, client, userdata, msg):
        if msg.topic not in self.ignored:
            print(msg.topic+" "+str(msg.payload))
            self.update_ws_clients(msg.payload)

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.passwd)
        self.client.connect(self.host, self.port, 60)
        self.client.loop_forever()

    def publish_event(self, evt, success):
        self.send(self.event_topic, json.dumps({
            "evt": evt,
            "clientId": self.client_id,
            "success": success,
        }))

    def publish_register(self):
        self.send(self.register_topic, json.dumps({
            "clientId": self.client_id
        }))
