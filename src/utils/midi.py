import threading
import mido
import pygame

from utils import get_logger

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
        get_logger().error(f"Error occurred while playing MIDI: {e}")
    finally:
        # Clean up Pygame
        pygame.mixer.quit()
        pygame.quit()

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