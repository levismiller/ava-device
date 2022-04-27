import os
import signal
import socket
import sys
import threading
from time import sleep

from dotenv import load_dotenv
from flask import Flask
from simple_websocket_server import WebSocketServer, WebSocket

from client_events import ClientEvents
from mqtt_client import MQTTClient

load_dotenv()

hardware = os.getenv('HARDWARE')
client_id = f"{hardware}-{socket.gethostname()}"

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

mqtt_client_thread = None
ws_server_thread = None
heartbeat_thread = None
ws_clients = []
mqtt = None
client_handler = ClientEvents(mqtt)


class WebsocketHandler(WebSocket):
    def handle(self):
        reply = client_handler.event(self.data)
        if reply:
            for client in ws_clients:
                client.send_message(reply)

    def connected(self):
        print(self.address, 'connected')
        for client in ws_clients:
            client.send_message(self.address[0] + u' - connected')
        ws_clients.append(self)

    def handle_close(self):
        ws_clients.remove(self)
        print(self.address, 'closed')
        for client in ws_clients:
            client.send_message(self.address[0] + u' - disconnected')


def update_ws_clients(msg):
    for client in ws_clients:
        client.send_message(msg)


def start_mqtt_client():
    global mqtt
    global update_ws_clients

    mqtt_user = "n3xus"
    mqtt_pwd = "n3xus"
    mqtt_host = "146.190.1.236"
    mqtt_port = 1883

    mqtt = MQTTClient(mqtt_user, mqtt_pwd, mqtt_host, client_id, update_ws_clients, mqtt_port)
    client_handler.mqtt = mqtt
    mqtt.connect()


def start_ws_server():
    server = WebSocketServer('localhost', 8765, WebsocketHandler)
    server.serve_forever()


def start_heartbeat():
    global mqtt
    while True:
        sleep(1)
        mqtt.publish_register()


def shutdown_services():
    mqtt_client_thread.join(1)
    ws_server_thread.join(1)
    heartbeat_thread.join(1)

    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, shutdown_services)

    mqtt_client_thread = threading.Thread(target=start_mqtt_client)
    mqtt_client_thread.setName('mqtt_client')
    mqtt_client_thread.daemon = False
    mqtt_client_thread.start()

    ws_server_thread = threading.Thread(target=start_ws_server)
    ws_server_thread.setName('ws_server')
    ws_server_thread.daemon = False
    ws_server_thread.start()

    heartbeat_thread = threading.Thread(target=start_heartbeat)
    heartbeat_thread.setName('heartbeat')
    heartbeat_thread.daemon = False
    heartbeat_thread.start()

    app.run(port=8000)
