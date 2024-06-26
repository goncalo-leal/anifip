import json
import threading
import time
import mido
import pygame
#import RPi.GPIO as GPIO
from utils import config
from utils import print_log_message
from utils import messages
from mqtt_client import client, mqtt, ack_event
import os
from pygame.locals import *


# Convert a MIDI message to a string
def msg_to_str(msg):
    return f"Message Type: {msg.type}, Note: {msg.note}, Velocity: {msg.velocity}\n"

# Convert note on messages with velocity 0 to note off messages,
# in order to support various MIDI devices 
def check_msg_type(msg):
        if msg.velocity == 0 and msg.type == 'note_on':
            return mido.Message('note_off', note=msg.note, velocity=0, time=msg.time)
        else:
            return msg

# Play MIDI file
def play_midi_file(midi_file="Vivaldi Winter (Allegro).mid", chunk_size=256):
    # msg_queue.put(f"Playing MIDI file: {midi_file}")
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    try:
        # Load MIDI file
        pygame.mixer.music.load(midi_file)

        # Play the MIDI file
        pygame.mixer.music.play()

        # Wait until music has finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

    except pygame.error as e:
       print_log_message("error", f"Error occurred while playing MIDI: {e}")
    finally:
        # Clean up Pygame
        pygame.mixer.quit()
        pygame.quit()

# If it is a note on message on low register, blink the LED
def led_blink_with_bass(midi_file="midi_files/Vivaldi Winter (Allegro).mid"):
    #create a new MIDI file with the track
    mid = mido.MidiFile(midi_file)

    i = 0  # Initialize the counter
    for msg in mid.play():
        # Check if the message is a note on message
        if msg.type == 'note_on':
            # Check if the message is in the low register
            if msg.note < config.BASS_THRESHOLD:
                i += 1  # Increment the counter
                print("LED Blinking ")
                print(f"Note: {msg.note}, Velocity: {msg.velocity}")
                # pwm.ChangeDutyCycle(100)  # Turn on the LED
                # time.sleep(0.1)  # Blink duration
                # pwm.ChangeDutyCycle(0)  # Turn off the LED
    
        # Check if the message is a note off message
        if msg.type == 'note_off':
            # Check if the message is in the low register
            if msg.note < config.BASS_THRESHOLD:
                #pwm.ChangeDutyCycle(0)  # Turn off the LED
                print("change duty cycle to 0")

# Execute actions based on the current action value
def execute_action(action, midi_file="midi_files/Vivaldi Winter (Allegro).mid"):
    # Check if the action is LED_BLINK_WITH_INPUT
    if action == "LED_BLINK_WITH_BASS":
        led_blink_with_bass(midi_file)


# Print messages of each track
def print_track_messages(track):
    print_log_message("info", f'Track: {track.name}')

    # Create a new MIDI file with the track
    mid = mido.MidiFile()
    mid.tracks.append(track)

    # Print messages in the track
    for msg in mid.play():
        print_log_message("info", f"[{track.name}] {msg}")
        print(f"[{track.name}] {msg}")
    
    print_log_message("info", f"End of track: {track.name}")



# Function to call the print_track_messages function for each track
def print_midi_file(midi_file="../midi_files/Vivaldi Winter (Allegro).mid"):
    # Load MIDI file
    mid = mido.MidiFile(midi_file)

    # Iterate over tracks and print messages in separate threads
    # threads = []
    # for i, track in enumerate(mid.tracks):
    #     thread = threading.Thread(target=print_track_messages, args=(track,))
    #     thread.start()
    #     threads.append(thread)

    # # Wait for all threads to finish
    # for thread in threads:
    #     thread.join()

    for msg in mid.play():
        print_log_message("info", f"{msg}")

# Function to call the execute_action function for each track 
def execute_by_midi_file(action,  midi_file="Vivaldi Winter (Allegro).mid"):

    # Load MIDI file
    mid = mido.MidiFile(midi_file)

    thread = threading.Thread(target=execute_action, args=(action,))
    thread.start()

    thread.join()

# Get midi input port
def get_input_port():
    print_log_message("info", "Getting available MIDI input ports...")

    # List available MIDI input ports
    print("Available MIDI input ports:")
    for port in mido.get_input_names():
        print(port)
    
    # Specify the name of the MIDI input port you want to open
    input_port_name = input("Enter the name of your MIDI input port: ")

    # Open the specified MIDI input port using the ALSA backend
    return mido.open_input(input_port_name)


#play_midi_thread = threading.Thread(target=print_midi_file)


def send_message_and_wait_for_ack(message, topic):
    ack_event.clear()  # Clear the event before sending a new message
    try:
        result = client.publish(topic, message)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print_log_message("error", f"Failed to publish message: {result.rc}")
        ack_event.wait()  # Wait for the ACK event
    except Exception as e:
        print_log_message("error", f"Error publishing message: {e}")
        raise




