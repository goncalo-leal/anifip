import base64
import mido
from utils import *
from Actions import *
import threading
import time
import pygame

command_mode = False
action = None
note = None
velocity = None
msg_type = None
chord_pressed = False



def play_midi_file(midi_file="Vivaldi Winter (Allegro).mid", chunk_size=256):
    print("Playing MIDI file:", midi_file)
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
        print("Error occurred while playing MIDI:", e)
    finally:
        # Clean up Pygame
        pygame.mixer.quit()
        pygame.quit()

# create thread to print track
def print_track_messages(track):
    print('Track {}: {}'.format(i, track.name))
    print('Track : ', track)
    for msg in track:
        print(msg)
        time.sleep(msg.time)
    


# List available MIDI input ports
print("Available MIDI input ports:")
for port in mido.get_input_names():
    print(port)

# Specify the name of the MIDI input port you want to open
input_port_name = input("Enter the name of your MIDI input port: ")

# Open the specified MIDI input port using the ALSA backend
input_port = mido.open_input(input_port_name, backend='alsa')

# MIDI buffer to store the messages and timestamps
midi_buffer = []

# Start the thread for processing MIDI messages
midi_thread = threading.Thread(target=play_midi_file)
midi_thread.daemon = True
midi_thread.start()

#open midi track
midi_file = "Vivaldi Winter (Allegro).mid"


#separate threads per instrument of the midi file
mid = mido.MidiFile(midi_file)

# Create a thread for each track to print the messages
threads = []
midi_thread = threading.Thread(target=play_midi_file)
midi_thread.daemon = True
midi_thread.start()

for i, track in enumerate(mid.tracks):
    thread = threading.Thread(target=print_track_messages, args=(track,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()


# Receive and print MIDI messages
for message in input_port:

    # Check if the received message is a control change message
    if message.type == 'control_change' and message.control == 115:
        midi_buffer = []
        # Update the command mode only when the control change message indicates the "ON" state
        command_mode = not command_mode if message.value == 127 else command_mode
        print("Command Mode:", "ON" if command_mode else "OFF")
    elif message.type == 'control_change' and message.control == 116:
        # Exit the loop
        break

    if message.type is 'note_on':
        msg = check_msg_type(message)
        note = msg.note
        velocity = msg.velocity
        msg_type = msg.type
        # Change the action based on the received message
        if command_mode and msg_type == 'note_on':
            # Perform a specific action when a note-on message is received in command mode
            if note == 60:
                action = Actions.LED_BLINK_WITH_INPUT
                print("Action:", action)

        
        # Print the received message
        print(msg_to_str(msg))

