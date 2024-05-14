import mido
import sounddevice as sd
import numpy as np
import time

# Function to check if there are notes playing
def check_notes_playing(messages):
    for msg in messages:
        if msg.type == 'note_on':
            return True
    return False

# Function to record MIDI playing
def record_midi(duration):
    messages = []
    def callback(indata, frames, time, status):
        if status:
            msg = mido.Message.from_bytes(status)
            messages.append(msg)

    with mido.open_input('Launchkey MK3 25:Launchkey MK3 25 LKMK3 MIDI In 36:0', backend='alsa') as port:
        with sd.InputStream(callback=callback):
            time.sleep(duration)
    return messages

# Main function
def main():
    print("Recording MIDI for 5 seconds...")
    messages = record_midi(5)

    if check_notes_playing(messages):
        print("Notes are playing!")
    else:
        print("No notes are playing.")

if __name__ == "__main__":
    main()
