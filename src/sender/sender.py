import threading
import json
import os
import time
from utils import print_log_message, config, midi, messages
from mqtt_client import client, ack_event, connect, mqtt

def wait_for_init_ack_and_start_threads(midi_file_path):
    print_log_message("info", "Waiting for ACK...")
    ack_event.wait(timeout=10)  # Block until the event is set or timeout occurs
    print_log_message("info", "ACK received, starting print and play threads")

# Connect to the MQTT broker
connect()

valid_action_keys = [60, 62]

# Load the MIDI file with error handling
midi_file_path = os.path.join("..", "midi_files", config.MIDI_FILE)
print(midi_file_path)
try:
    with open(midi_file_path, "rb") as file:
        midi_data = file.read()
except FileNotFoundError:
    print_log_message("error", f"MIDI file not found: {midi_file_path}")
    raise
except Exception as e:
    print_log_message("error", f"Error reading MIDI file: {e}")
    raise

# Create the JSON Message
broadcast_data_msg_dict = messages.create_message("BROADCAST_DATA", data=midi_file_path)
broadcast_data_msg = json.dumps(broadcast_data_msg_dict)

# Publish the MIDI message with error handling
try:
    result = client.publish(config.TOPIC_MASTER_OUT, broadcast_data_msg)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print_log_message("error", f"Failed to publish MIDI message: {result.rc}")
except Exception as e:
    print_log_message("error", f"Error publishing MIDI message: {e}")
    raise

print_log_message("info", "MIDI file sent")

# Thread to wait for ACK init and start print and play threads
wait_thread = threading.Thread(target=wait_for_init_ack_and_start_threads, args=(midi_file_path,))
wait_thread.daemon = True
wait_thread.start()

input_port = midi.get_input_port()

def read_midi_messages(input_port, command_mode=False):
    last_control_message = None
    debounce_time = 0.2  # 200 ms debounce time
    midi_file_path2 = os.path.join("..", "midi_files", config.MIDI_FILE2)

    while True:
        message = input_port.receive()
        if message.type == 'clock':
            continue

        print(f"Received MIDI message: {message}")

        if message.type == 'control_change':
            current_time = time.time()
            if last_control_message and current_time - last_control_message < debounce_time:
                continue
            last_control_message = current_time

            if message.control == 104:
                if message.value == 127:
                    command_mode = not command_mode
                    print("Command Mode:", "ON" if command_mode else "OFF")

            elif message.control == 116:
                break

            if command_mode:
                if message.control == 115 and message.value != 0:
                    ack_event.clear()
                    msg = messages.create_message("BROADCAST_CONTROL", control_type="START_PLAYBACK")
                    start_playback = json.dumps(msg)
                    try:
                        result = client.publish(config.TOPIC_MASTER_OUT, start_playback)
                        if result.rc != mqtt.MQTT_ERR_SUCCESS:
                            print("Failed to publish MIDI message: %d", result.rc)
                        else:
                            if not ack_event.wait(timeout=10):  # Wait with a timeout
                                print("Timeout waiting for ACK")
                    except Exception as e:
                        print("Error publishing MIDI message: %s", e)
                        raise

                if message.control == 103 and message.value != 0:
                    ack_event.clear()
                    upload_new_music_msg_dict = messages.create_message("BROADCAST_DATA", data=midi_file_path2)
                    upload_new_music_msg = json.dumps(upload_new_music_msg_dict)

                    try:
                        result = client.publish(config.TOPIC_MASTER_OUT, upload_new_music_msg)
                        if result.rc != mqtt.MQTT_ERR_SUCCESS:
                            print_log_message("error", f"Failed to publish MIDI message: {result.rc}")
                        else:
                            if not ack_event.wait(timeout=10):  # Wait with a timeout
                                print("Timeout waiting for ACK")
                    except Exception as e:
                        print_log_message("error", f"Error publishing MIDI message: {e}")
                        raise

                    print_log_message("info", "MIDI file2 sent")

                    msg = messages.create_message("BROADCAST_CONTROL", control_type="START_PLAYBACK")
                    start_playback = json.dumps(msg)

                    try:
                        result = client.publish(config.TOPIC_MASTER_OUT, start_playback)
                        if result.rc != mqtt.MQTT_ERR_SUCCESS:
                            print("Failed to publish MIDI message: %d", result.rc)
                        else:
                            print("Entrei aqui CHANGE MUSIC")
                            if not ack_event.wait(timeout=10):  # Wait with a timeout
                                print("Timeout waiting for ACK")
                    except Exception as e:
                        print("Error publishing MIDI message: %s", e)
                        raise

        if message.type == 'note_on' and command_mode:
            if message.velocity != 0:
                if message.note == 60:
                    ack_event.clear()
                    action = "LED_BLINK_WITH_BASS"
                if message.note == 62:
                    ack_event.clear()
                    action = "LED_BLINK_WITH_BASS_X2"
                if message.note in valid_action_keys:
                    msg = json.dumps(messages.create_message("ACTION", action, slave_type="LED"))
                    try:
                        result = client.publish(config.TOPIC_MASTER_OUT, msg)
                        if result.rc != mqtt.MQTT_ERR_SUCCESS:
                            print("Failed to publish MIDI message: %d", result.rc)
                        else:
                            print("Entrei aqui NOTE ON")
                            if not ack_event.wait(timeout=10):  # Wait with a timeout
                                print("Timeout waiting for ACK")
                    except Exception as e:
                        print("Error publishing MIDI message: %s", e)
                        raise

# Start the thread for reading MIDI messages
read_thread = threading.Thread(target=read_midi_messages, args=(input_port, False))
read_thread.daemon = True
read_thread.start()

# Wait for the threads to finish
read_thread.join()
wait_thread.join()

# Ensure the client loop is still running
def keep_client_loop_running():
    while True:
        print("CLIENT_LOOP thread")
        if not client.is_connected():
            print_log_message("error", "MQTT client disconnected. Reconnecting...")
            connect()
        time.sleep(5)

client_thread = threading.Thread(target=keep_client_loop_running)
client_thread.daemon = True
client_thread.start()
