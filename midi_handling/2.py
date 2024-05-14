import mido
import threading
import time
import pygame
import queue

command_mode = False
action = None

# Message queue
msg_queue = queue.Queue()

# Function to read MIDI messages from the input port
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
        msg_queue.put(f"Received MIDI message: {message}")

# Function to print messages of each track
def print_track_messages(track):
    msg_queue.put(f'Track: {track.name}')

    # Create a new MIDI file with the track
    mid = mido.MidiFile()
    mid.tracks.append(track)

    # Print messages in the track
    for msg in mid.play():
        msg_queue.put(f"[{track.name}] {msg}")
    
    msg_queue.put(f"End of track: {track.name}")

# Function to play MIDI file
def play_midi_file(midi_file="Vivaldi Winter (Allegro).mid", chunk_size=256):
    msg_queue.put(f"Playing MIDI file: {midi_file}")
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
        msg_queue.put(f"Error occurred while playing MIDI: {e}")
    finally:
        # Clean up Pygame
        pygame.mixer.quit()
        pygame.quit()

# Function to call the print_track_messages function for each track
def print_midi_file(midi_file="Vivaldi Winter (Allegro).mid"):
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

# List available MIDI input ports
print("Available MIDI input ports:")
for port in mido.get_input_names():
    print(port)

# Specify the name of the MIDI input port you want to open
input_port_name = input("Enter the name of your MIDI input port: ")

# Open the specified MIDI input port using the ALSA backend
input_port = mido.open_input(input_port_name, backend='alsa')

# Start the thread for printing the MIDI file
print_thread = threading.Thread(target=print_midi_file)
print_thread.daemon = True
print_thread.start()

# Start the thread for playing the MIDI file
play_thread = threading.Thread(target=play_midi_file)
play_thread.daemon = True
play_thread.start()

# Start the thread for reading MIDI messages
read_thread = threading.Thread(target=read_midi_messages, args=(input_port, command_mode))
read_thread.daemon = True
read_thread.start()

# Receive and print messages
while True:
    try:
        msg = msg_queue.get(timeout=1)
        print(msg)
    except queue.Empty:
        pass
    except KeyboardInterrupt:
        break
