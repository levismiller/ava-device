from mqtt_client import MQTTClient
import sys
import signal
import threading
from time import sleep
import socketserver
from http_server import MyHttpRequestHandler
from simple_websocket_server import WebSocketServer, WebSocket
from client_events import ClientEvents
import socket
import os
from dotenv import load_dotenv

load_dotenv()

hardware = os.getenv('HARDWARE')
client_id = f"{hardware}-{socket.gethostname()}"

mqtt_client_run = True
mqtt_client_thread = None

ws_server_run = True
ws_server_thread = None

http_server_run = True
http_server_thread = None

heartbeat_run = True
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


def start_http_server():
    handler_object = MyHttpRequestHandler
    PORT = 80
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    my_server.serve_forever()


def start_heartbeat():
    while True:
        sleep(1)
        mqtt.publish_register()


def shutdown_services():
    mqtt_client_run = False
    mqtt_client_thread.join(1)

    ws_server_run = False
    ws_server_thread.join(1)

    http_server_run = False
    http_server_thread.join(1)

    heartbeat_run = False
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

    http_server_thread = threading.Thread(target=start_http_server)
    http_server_thread.setName('http_server')
    http_server_thread.daemon = False
    http_server_thread.start()

    heartbeat_thread = threading.Thread(target=start_heartbeat)
    heartbeat_thread.setName('heartbeat')
    heartbeat_thread.daemon = False
    heartbeat_thread.start()
