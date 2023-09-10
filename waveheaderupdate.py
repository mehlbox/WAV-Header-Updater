import struct
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.font as tkFont

def update_wav_header():
    try:
        input_file_path = input_file_path_entry.get()
        num_channels = int(num_channels_var.get())
        sample_rate = int(sample_rate_var.get())
        bits_per_sample = int(bits_per_sample_var.get())
    
        file_size = os.path.getsize(input_file_path)
        header_size = 44

        with open(input_file_path, 'r+b') as file:
            header_data = file.read(header_size)
            data_size = file_size - header_size
            new_header = struct.pack(
                '<4sI4s4sIHHIIHH4sI',
                b'RIFF',
                file_size - 8,
                b'WAVE',
                b'fmt ',
                16,
                1,
                num_channels,
                sample_rate,
                sample_rate * num_channels * bits_per_sample // 8,
                num_channels * bits_per_sample // 8,
                bits_per_sample,
                b'data',
                data_size
            )
            file.seek(0)
            file.write(new_header)

            result_label.config(text=f"The header of file '{input_file_path}' was updated with the given information.")
    except:
        result_label.config(text=f"Could not updated header. Are all forms filled?")


root = tk.Tk()
root.title("WAV Header Updater")

style = ttk.Style()
custom_font = tkFont.Font(family="Helvetica", size=12)
style.configure('.', font=custom_font)
style.configure('TButton', padding=10, relief="flat")
style.map('TButton')

frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=20, pady=20)

ttk.Label(frame, text="File:").grid(row=0, column=0, sticky="w")
input_file_path_entry = ttk.Entry(frame, width=45)
input_file_path_entry.grid(row=1, column=0, columnspan=2, )
ttk.Button(frame, text="Browse", command=lambda: input_file_path_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2, rowspan=2)

ttk.Label(frame, text="Number of Channels:").grid(row=2, column=0, sticky="w")
num_channels_var = tk.StringVar()
num_channels_dropdown = ttk.Combobox(frame, textvariable=num_channels_var, values=[1, 2], font=custom_font)
num_channels_dropdown.grid(row=2, column=1)

ttk.Label(frame, text="Sample Rate:").grid(row=3, column=0, sticky="w")
sample_rate_var = tk.StringVar()
sample_rate_dropdown = ttk.Combobox(frame, textvariable=sample_rate_var, values=[44100, 48000], font=custom_font)
sample_rate_dropdown.grid(row=3, column=1)

ttk.Label(frame, text="Bit Depth:").grid(row=4, column=0, sticky="w")
bits_per_sample_var = tk.StringVar()
bits_per_sample_dropdown = ttk.Combobox(frame, textvariable=bits_per_sample_var, values=[16, 24], font=custom_font)
bits_per_sample_dropdown.grid(row=4, column=1)

update_button = ttk.Button(frame, text="Update Header", command=update_wav_header)
update_button.grid(row=5, columnspan=3)

result_label = ttk.Label(frame, text="")
result_label.grid(row=6, columnspan=3)

root.mainloop()
