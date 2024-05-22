import base64
import json
import random
from paho.mqtt import client as mqtt
import time
from datetime import datetime
import threading
import os
# Import the logger and configuration from the utils package
from utils import get_logger
from utils import config
from utils import midi
from utils import messages

# Initialize logger
log = get_logger()

midi_file_path = os.path.join("midi_files", config.MIDI_FILE)

# Generate a Client ID with the publish prefix.
client_id = f'worker-{random.randint(0, 1000)}'

# Initialize the MQTT client
client = mqtt.Client(client_id)

# Connect to the MQTT broker
client.connect(config.MQTT_BROKER, config.MQTT_PORT)

# Subscribe to the MIDI topic
client.subscribe(config.TOPIC_MASTER_OUT)

# Event to signal the thread to stop
stop_event = threading.Event()

# Define a function that will be executed in a separate thread
def delayed_action(delay, action):
    global stop_event
    start_time = time.time()
    
    while time.time() - start_time < delay:
        if stop_event.is_set():
            return
        time.sleep(0.1)
    
    if not stop_event.is_set():
        midi.execute_action(midi_file_path, stop_event)  # Include stop_event here

# Ensure the midi_files directory exists
try:
    with open(f"midi_files/{config.MIDI_FILE}", "wb") as file:
        pass
except FileNotFoundError:
    import os
    os.makedirs("midi_files")

# Initialize a variable to keep track of the playback thread
playback_thread = None

def on_message(client, userdata, message):
    global playback_thread
    
    print(message.payload)
    
    # Decode the message, assuming it's a JSON payload
    try:
        message = json.loads(message.payload)
        ack_msg, delay = messages.process(message)
        client.publish(config.TOPIC_MASTER_IN, json.dumps(ack_msg))
        print(message)
        if ack_msg and delay is None:
            log.info("Sending ACK")
            return 
        if delay:
            timestamp = time.time()
            readable_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            print(f"{readable_timestamp} - Will do my action after {delay} seconds delay")
            
            # Stop the current playback thread if it exists and is alive
            if playback_thread and playback_thread.is_alive():
                stop_event.set()
                playback_thread.join()
            
            # Clear the stop event for the new thread
            stop_event.clear()
            
            # Create a new playback thread
            playback_thread = threading.Thread(target=delayed_action, args=(delay, midi.current_action))
            playback_thread.start()
        else:
            if playback_thread and playback_thread.is_alive():
                stop_event.set()
                playback_thread.join()
            playback_thread = threading.Thread(target=delayed_action, args=(0, midi.current_action))     
            playback_thread.start()
    except Exception as e:
        log.error(f"Error processing message: {e}")

# Set the callback for when a message is received
client.on_message = on_message

# Start the loop
client.loop_forever()

# TODO: Make code more robust by adding error handling and reconnecting to the broker
# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python