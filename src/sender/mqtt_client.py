import threading
from paho.mqtt import client as mqtt
from utils import print_log_message, config, messages
import json

ack_event = threading.Event()

# Initialize the MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print_log_message("info", "Connected to MQTT Broker!")
    else:
        print_log_message("error", f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    print_log_message("info", f"Message received on topic {msg.topic}: {msg.payload}")
    try:
        message = json.loads(msg.payload)
        if messages.ack_checker(message):
            ack_event.set()
    except Exception as e:
        print_log_message("error", f"Error processing message: {e}")

client.on_connect = on_connect
client.on_message = on_message

def connect():
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_start()
        client.subscribe(config.TOPIC_MASTER_IN)
    except Exception as e:
        print_log_message("error", f"Failed to connect to MQTT Broker: {e}")
        raise

# Expose client and ack_event for use in other modules
__all__ = ["client", "ack_event", "connect"]