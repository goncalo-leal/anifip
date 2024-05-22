import threading
import time
import mido
import traceback
import pygame
import RPi.GPIO as GPIO
from utils import config
from utils import get_logger


current_action = config.START_ACTION

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(config.LED_PIN1, GPIO.OUT)
GPIO.setup(config.LED_PIN2, GPIO.OUT)  # Set LED 2 pin as output

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
        
def set_current_action(new_current_action):
    global current_action
    current_action = new_current_action

# Function to initialize GPIO
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD depending on your pin numbering preference
    GPIO.setup(config.LED_PIN1, GPIO.OUT)
    GPIO.setup(config.LED_PIN2, GPIO.OUT)  # Set LED 2 pin as output

# Function to clean up GPIO
def cleanup_gpio():
    GPIO.cleanup()

# Function to turn on an LED
def turn_on_led(pin):
    GPIO.output(pin, GPIO.HIGH)  # Set the pin to HIGH to turn on the LED

# Function to turn off an LED
def turn_off_led(pin):
    GPIO.output(pin, GPIO.LOW)  # Set the pin to LOW to turn off the LED


def execute_action(midi_file, stop_event):
    global current_action
    cleanup_gpio()  # Ensure GPIO is cleaned up after execution
    initialize_gpio()  # Ensure GPIO is initialized

    try:
        mid = mido.MidiFile(midi_file)

        for i, track in enumerate(mid.tracks):
            channels = set ()
            for msg in track:
                if msg.type in ['note_on', 'note_off']:
                    channels.add(msg.channel)
            channels_list = ', '.join(str(channel) for channel in channels)
            print(f"Track{i} ({track.name}): Channels {channels_list}")


        for msg in mid.play():
            if stop_event.is_set():
                turn_off_led(config.LED_PIN1)
                break

            if current_action == "LED_BLINK_WITH_BASS":
                if msg.type == 'note_on' and msg.velocity != 0 and msg.channel == 1:
                    #if msg.note < config.BASS_THRESHOLD:
                    print(f"LED_BLINK_WITH_BASS: LED Blinking for note {msg.note}")
                    turn_on_led(config.LED_PIN1)
                        
                elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0) and msg.channel == 1):
                    print(f"LED_BLINK_WITH_BASS: LED Turning off for note {msg.note}")
                    turn_off_led(config.LED_PIN1)

            elif current_action == "LED_BLINK_WITH_BASS_X2":
                if msg.type == 'note_on' and msg.velocity != 0:
                    if msg.note < config.BASS_THRESHOLD:
                        print(f"LED_BLINK_WITH_BASS_X2: LED Blinking for note {msg.note}")
                        turn_on_led(config.LED_PIN1)

                elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                    if msg.note < config.BASS_THRESHOLD:
                        print(f"LED_BLINK_WITH_BASS_X2: LED Turning off for note {msg.note}")
                        turn_off_led(config.LED_PIN1)
    except Exception as e:
        print(f"Error occurred while loading MIDI file: {e}")



# Print messages of each track
def print_track_messages(track):
    get_logger().info(f'Track: {track.name}')

    # Create a new MIDI file with the track
    mid = mido.MidiFile()
    mid.tracks.append(track)

    # Print messages in the track
    for msg in mid.play():
        get_logger().info(f"[{track.name}] {msg}")
        print(f"[{track.name}] {msg}")
    
    get_logger().info(f"End of track: {track.name}")

# Function to call the print_track_messages function for each track
def print_midi_file(midi_file):
    # Load MIDI file
    mid = mido.MidiFile(midi_file)

    # Iterate over tracks and print messages in separate threads
    threads = []
    for i, track in enumerate(mid.tracks):
        thread = threading.Thread(target=print_track_messages, args=(track,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()



# Get midi input port
def get_input_port():
    get_logger().info("Getting available MIDI input ports...")

    # List available MIDI input ports
    print("Available MIDI input ports:")
    for port in mido.get_input_names():
        print(port)
    
    # Specify the name of the MIDI input port you want to open
    input_port_name = input("Enter the name of your MIDI input port: ")

    # Open the specified MIDI input port using the ALSA backend
    return mido.open_input(input_port_name)


# Read MIDI messages from the input port
def read_midi_messages(input_port, command_mode=False):
    while True:
        # Receive MIDI messages
        message = input_port.receive()

        # Check if the received message is a control change message
        if message.type == 'control_change' and message.control == 115:
            command_mode = not command_mode if message.value == 127 else command_mode
            print("Command Mode:", "ON" if command_mode else "OFF")
        elif message.type == 'control_change' and message.control == 116:
            break

        if message.type == 'note_on':
            # Change the action based on the received message
            if command_mode:
                if message.note == 60:
                    action = "LED_BLINK_WITH_INPUT"
                    print("Action:", action)

        # Ignore clock messages
        if message.type == 'clock':
            continue

        # Put the received message in the queue
        print(f"Received MIDI message: {message}")