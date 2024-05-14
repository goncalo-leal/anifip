"""
Receive mqtt messages encoded in protobuf format and deserialize them.
"""

import base64
import random
import threading
import time
from paho.mqtt import client as mqtt

import messages.midi_pb2 as midi_pb2

# Import the logger and configuration from the utils package
from utils import get_logger
from utils import config
from utils import midi

# Initialize logger
log = get_logger()

# Generate a Client ID with the publish prefix.
client_id = f'worker-{random.randint(0, 1000)}'

# Initialize the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(config.MQTT_BROKER, config.MQTT_PORT)

# Subscribe to the MIDI topic
client.subscribe(config.TOPIC_MIDI)

# Callback for when a message is received
def on_message(client, userdata, message):
    print(message.payload)

    # Deserialize the MIDI message
    midi_message = midi_pb2.InitMessage()
    midi_message.ParseFromString(message.payload)
    
    # Decode the MIDI file
    midi_data = base64.b64decode(midi_message.midiFile)

    # Check if midi_files directory exists
    try:
        with open(f"midi_files/{config.MIDI_FILE}", "wb") as file:
            pass
    except FileNotFoundError:
        import os
        os.makedirs("midi_files")
    
    # Save the MIDI file
    with open(f"midi_files/{config.MIDI_FILE}", "wb") as file:
        file.write(midi_data)
    
    # Log the timestamp and NTP offset
    log.info("Timestamp: %s", midi_message.timestamp)
    log.info("NTP Offset: %s", midi_message.ntpOffset)

    print ("MIDI file received")

    midi.play_midi_file(f"midi_files/{config.MIDI_FILE}")

# Set the callback for when a message is received
client.on_message = on_message

# Start the loop
client.loop_forever()

# TODO: Make code more robust by adding error handling and reconnecting to the broker
# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
