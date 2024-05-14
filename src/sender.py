"""
Main sender module

This module is responsible for sending the MIDI file to the worker nodes. It uses the Pygame library 
to play the MIDI file and the Mido library to handle MIDI commands. The sender uses protobufs to 
serialize and deserialize the ad-hoc network messages.
"""

import base64
import threading
import time
from paho.mqtt import client as mqtt

import messages.midi_pb2 as midi_pb2

from utils import get_logger
from utils import config
from utils import midi

# Initialize logger
log = get_logger()

# Initialize the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(config.MQTT_BROKER, config.MQTT_PORT)

# Send protobuf message with the midi file encoded in base64
# start the loop
client.loop_start()

# Load the MIDI file
with open(f"../midi_files/{config.MIDI_FILE}", "rb") as file:
    midi_data = file.read()

# Create a MIDI message with the MIDI file encoded in base64, timestamp and the ntp offset
midi_message = midi_pb2.InitMessage()
midi_message.midiFile = base64.b64encode(midi_data)
midi_message.timestamp = time.time()
midi_message.ntpOffset = 0 # TODO: Get the NTP offset

# Serialize the MIDI message
midi_message_serialized = midi_message.SerializeToString()

# Publish the MIDI message
client.publish(config.TOPIC_MIDI, midi_message_serialized)

# Log the timestamp and NTP offset
log.info("Timestamp: %s", midi_message.timestamp)
log.info("NTP Offset: %s", midi_message.ntpOffset)

log.info("MIDI file sent")

# TODO: Send the MIDI file to the worker nodes
# TODO: Wait for the worker nodes to receive the MIDI file and are ready to play it
# TODO: Send the play command to the worker nodes (with timestamp and ntp offset for synchronization)

# Start the thread for printing the MIDI file
print_thread = threading.Thread(target=midi.print_midi_file, args=(f"../midi_files/{config.MIDI_FILE}",))
print_thread.daemon = True
print_thread.start()

# Start the thread for playing the MIDI file
play_thread = threading.Thread(target=midi.play_midi_file, args=(f"../midi_files/{config.MIDI_FILE}",))
play_thread.daemon = True
play_thread.start()

input_port = midi.get_input_port()

# Start the thread for reading MIDI messages
read_thread = threading.Thread(target=midi.read_midi_messages, args=(input_port, False))
read_thread.daemon = True
read_thread.start()

# TODO: Stay alive to keep sending commands

# Wait for the threads to finish
print_thread.join()
play_thread.join()
read_thread.join()
