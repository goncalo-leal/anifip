import base64
import mido
from Actions import *
from pydub import AudioSegment
import io
import numpy as np
import fluidsynth
import time

pressed_notes = set()


# Convert note on messages with velocity 0 to note off messages,
# in order to support various MIDI devices 
def check_msg_type(msg):
        if msg.velocity == 0 and msg.type == 'note_on':
            return mido.Message('note_off', note=msg.note, velocity=0, time=msg.time)
        else:
            return msg

# Process a MIDI message
def is_chord_pressed(msg):
    global pressed_notes, chord_pressed
    if msg.type == 'note_on':
        pressed_notes.add(msg.note)
    elif msg.type == 'note_off':
        if msg.note in pressed_notes:
            pressed_notes.remove(msg.note)
    # Print the currently pressed notes (chord)

    if(len(pressed_notes) == 0):
        print("Current Chord: None")
        return False
    elif len(pressed_notes) > 1:
        print("Current Chord:", sorted(pressed_notes))
        return True

def send_msg(msg, action):
    if action == Actions.LED_BLINK_WITH_INPUT:
        print("Action:", action )

    print(msg_to_json(msg))


def convert_midi_to_audio(midi_buffer, soundfont_path='Essential Keys-sforzando-v9.6.sf2'):
    # Initialize FluidSynth
    fs = fluidsynth.Synth()
    fs.start()

    # Load soundfont
    sfid = fs.sfload(soundfont_path)
    fs.program_select(0, sfid, 0, 0)

    audio_samples = []

    # Sort MIDI messages by timestamp
    midi_buffer.sort(key=lambda x: x[1])

    # Initialize start time
    start_time = time.time()

    # Iterate over MIDI messages in the buffer and synthesize audio
    for msg, timestamp in midi_buffer:
        # Calculate time to wait before processing the message
        wait_time = timestamp - start_time
        if wait_time > 0:
            time.sleep(wait_time)
        start_time = timestamp
        
        if msg.type == 'note_on':
            fs.noteon(0, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            fs.noteoff(0, msg.note)
        
        # Get audio samples from the synthesizer
        audio = fs.get_samples()
        audio_samples.append(audio)
        
    # Concatenate audio samples into a single numpy array
    audio_data = np.concatenate(audio_samples)

    fs.delete()
    
    return audio_data

def convert_audio_to_base64(audio_data):
    try:
        # Convert the NumPy array to raw audio data
        raw_audio = audio_data.astype(np.int16).tobytes()

        # Encode the raw audio data as base64
        encoded_audio = base64.b64encode(raw_audio)

        return encoded_audio

    except Exception as e:
        print("Error during audio conversion:", e)
        return None

def msg_to_json(msg):
    return msg.dict()


# Convert a MIDI message to a string
def msg_to_str(msg):
    return f"Message Type: {msg.type}, Note: {msg.note}, Velocity: {msg.velocity}\n"