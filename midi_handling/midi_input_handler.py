import base64
import mido
from utils import *
from Actions import *

command_mode = False
action = None
note = None
velocity = None
msg_type = None
chord_pressed = False


# List available MIDI input ports
print("Available MIDI input ports:")
for port in mido.get_input_names():
    print(port)


# Specify the name of the MIDI input port you want to open
input_port_name = input("Enter the name of your MIDI input port: ")

# Open the specified MIDI input port using the ALSA backend
input_port = mido.open_input(input_port_name, backend='alsa')

#MIDI buffer to store the messages
midi_buffer = []

# Receive and print MIDI messages



for message in input_port:

    # Check if the received message is a control change message
    if message.type == 'control_change' and message.control == 115:
        # Update the command mode only when the control change message indicates the "ON" state
        command_mode = not command_mode if message.value == 127 else command_mode
        print("Command Mode:", "ON" if command_mode else "OFF")
    elif message.type == 'control_change' and message.control == 116:
        # get out of the loop
        break


    if message.type is 'note_on':
        msg = check_msg_type(message)
        note = msg.note
        velocity = msg.velocity
        msg_type = msg.type
        #Change the action based on the received message
        if command_mode and msg_type == 'note_on':
            # Perform a specific action when a note-on message is received in command mode
            if note == 60:
                action = Actions.LED_BLINK_WITH_INPUT
        
        # Process the midi message
        elif not command_mode:
            # Get if chord is pressed
            chord_pressed = is_chord_pressed(msg)
            midi_buffer.append(msg)
            #if buffer is full, convert to audio
            if len(midi_buffer) == 5:
                print("MIDI buffer:", midi_buffer)
                audio_stream = convert_midi_to_audio(midi_buffer)
                print("Audio stream:", audio_stream)
                #TODO: evaluate the audio stream in order to create metadata that will
                #be sent in a JSON format

                # Convert audio stream to base64
                encoded_audio = convert_audio_to_base64(audio_stream)
                print("Base64 encoded audio:", encoded_audio)
                
                midi_buffer = []
            # Dump Json with the message
            send_msg(msg, action)

        # Print the received message
        print(msg_to_str(msg))

        
