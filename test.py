import tkinter as tk
from tkinter import ttk
import pyttsx3

def on_speak():
    text = text_entry.get("1.0", tk.END).strip()
    if text:
        engine.setProperty('rate', speed_var.get())
        engine.setProperty('volume', volume_var.get())
        engine.say(text)
        engine.runAndWait()

# Initialize TTS engine
engine = pyttsx3.init()

# Create main window
root = tk.Tk()
root.title("Text-to-Speech with Speed and Volume Control")

# Text entry widget
text_entry = tk.Text(root, wrap=tk.WORD, height=10, width=50)
text_entry.pack(pady=10)

# Speed control slider label
speed_label = ttk.Label(root, text="Speed (words per minute)")
speed_label.pack(pady=5)

# Speed control slider
speed_var = tk.IntVar()
speed_slider = ttk.Scale(root, from_=50, to_=300, orient='horizontal', variable=speed_var)
speed_slider.set(150)  # Default speed
speed_slider.pack(pady=5)

# Volume control slider label
volume_label = ttk.Label(root, text="Volume")
volume_label.pack(pady=5)

# Volume control slider
volume_var = tk.DoubleVar()
volume_slider = ttk.Scale(root, from_=0.0, to_=1.0, orient='horizontal', variable=volume_var)
volume_slider.set(1.0)  # Default volume
volume_slider.pack(pady=5)

# Speak button
speak_button = ttk.Button(root, text="Speak", command=on_speak)
speak_button.pack(pady=10)

# Run the main loop
root.mainloop()

