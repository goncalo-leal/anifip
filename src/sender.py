"""
Main sender module

This module is responsible for sending the MIDI file to the worker nodes. It uses the Pygame library 
to play the MIDI file and the Mido library to handle MIDI commands. The sender uses protobufs to 
serialize and deserialize the ad-hoc network messages.
"""

import base64
import threading
import time
import json
import os
from paho.mqtt import client as mqtt


from utils import get_logger
from utils import config
from utils import midi
from utils import messages

# Initialize logger
log = get_logger()
broadcast_data_msg_sqc_number = 0

# Initialize the MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("Connected to MQTT Broker!")
    else:
        log.error("Failed to connect, return code %d\n", rc)

client.on_connect = on_connect

# Initialize the ACK event
ack_event = threading.Event()

# Define the on_message callback
def on_message(client, userdata, msg):
    global broadcast_data_msg_sqc_number
    log.info("Message received on topic %s: %s", msg.topic, msg.payload)
    try:
        message = json.loads(msg.payload)
        ack_check = messages.ack_checker(message)
        if ack_check:
            ack_event.set()
    except Exception as e:
        log.error("Error processing message: %s", e)

client.on_message = on_message


def wait_for_ack_and_start_threads(midi_file_path):
    log.info("Waiting for ACK...")
    ack_event.wait()  # Block until the event is set
    log.info("ACK received, starting print and play threads")

    # Start the thread for printing the MIDI file
    print_thread = threading.Thread(target=midi.print_midi_file, args=(midi_file_path,))
    print_thread.daemon = True
    print_thread.start()

    # Start the thread for playing the MIDI file
    play_thread = threading.Thread(target=midi.play_midi_file, args=(midi_file_path,))
    play_thread.daemon = True
    play_thread.start()

    # Wait for the threads to finish
    print_thread.join()
    play_thread.join()


# Connect to the MQTT broker with error handling
try:
    client.connect(config.MQTT_BROKER, config.MQTT_PORT)
    client.loop_start()
    client.subscribe(config.TOPIC_ACK)
except Exception as e:
    log.error("Failed to connect to MQTT Broker: %s", e)
    raise


# Load the MIDI file with error handling
midi_file_path = os.path.join("..", "midi_files", config.MIDI_FILE)
try:
    with open(midi_file_path, "rb") as file:
        midi_data = file.read()
except FileNotFoundError:
    log.error("MIDI file not found: %s", midi_file_path)
    raise
except Exception as e:
    log.error("Error reading MIDI file: %s", e)
    raise


# Create the JSON Message
broadcast_data_msg = messages.create_message("BROADCAST_DATA", data=base64.b64encode(midi_data))
print(broadcast_data_msg)
broadcast_data_msg_sqc_number = broadcast_data_msg.get("sequence_number")
# Publish the MIDI message with error handling
try:
    result = client.publish(config.TOPIC_MIDI, broadcast_data_msg)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        log.error("Failed to publish MIDI message: %d", result.rc)
except Exception as e:
    log.error("Error publishing MIDI message: %s", e)
    raise

log.info("MIDI file sent")

# TODO: Send the MIDI file to the worker nodes

# TODO: Wait for the worker nodes to receive the MIDI file and are ready to play it
# TODO: Send the play command to the worker nodes (with timestamp and ntp offset for synchronization)

# Thread to wait for ACK and start print and play threads
wait_thread = threading.Thread(target=wait_for_ack_and_start_threads)
wait_thread.daemon = True
wait_thread.start()
input_port = midi.get_input_port()


# Start the thread for reading MIDI messages
read_thread = threading.Thread(target=midi.read_midi_messages, args=(input_port, False))
read_thread.daemon = True
read_thread.start()

# TODO: Stay alive to keep sending commands

# Wait for the threads to finish
read_thread.join()
wait_thread.join()