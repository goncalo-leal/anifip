import mido
import random
import threading
import tkinter as tk

# Function to handle MIDI messages
def handle_midi(file_path):
    # GUI Setup
    root = tk.Tk()
    root.title("MIDI Player")
    canvas = tk.Canvas(root, width=500, height=500)
    canvas.pack()

    midi_thread = threading.Thread(target=iterate_midi, args=(file_path, canvas, draw_shape,))
    midi_thread.start()

    # Run the GUI
    root.mainloop()

def iterate_midi(file_path, canvas, draw_shape):
    # Load MIDI file
    mid = mido.MidiFile(file_path)

    # Iterate over MIDI messages
    for msg in mid.play():
        if msg.type == 'note_on':
            note = msg.note
            velocity = msg.velocity
            draw_shape(canvas, note, velocity)

def draw_shape(canvas, note, velocity):
    canvas.delete("all")  # Clear previous shapes
    shape_size = note  # Size = note value
    x = random.randint(0, canvas.winfo_reqwidth() - shape_size)
    y = random.randint(0, canvas.winfo_reqheight() - shape_size)
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))  # Random hex color
    shape_type = random.choice(['oval', 'rectangle', 'polygon'])  # Random shape type
    if shape_type == 'oval':
        canvas.create_oval(x, y, x + shape_size, y + shape_size, fill=color)
    elif shape_type == 'rectangle':
        canvas.create_rectangle(x, y, x + shape_size, y + shape_size, fill=color)
    else:
        # Generate random points for polygon
        num_points = random.randint(3, 8)  # Random number of points between 3 and 8
        points = [(random.randint(x, x + shape_size), random.randint(y, y + shape_size)) for _ in range(num_points)]
        canvas.create_polygon(points, fill=color)

# Path to the MIDI file
file_path = "./Vivaldi Winter (Allegro)_GrandPiano.mid"

# Play MIDI file
handle_midi(file_path)
