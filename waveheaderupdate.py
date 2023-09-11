import struct
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.font as tkFont

header_size = 0
valid_wave = False

def get_spec():
    global header_size, valid_wave
    input_file_path_entry.delete(0, 'end')
    input_file_path_entry.insert(0, filedialog.askopenfilename())
    try:
        input_file_path = input_file_path_entry.get() 
        header_size = 0
        with open(input_file_path, 'r+b') as file:
            riff_chunk, chunk_size, wave_format = struct.unpack('<4sI4s', file.read(12))
            header_size += 12

            if riff_chunk != b'RIFF' or wave_format != b'WAVE':
                valid_wave = False
                raise ValueError("Not a valid WAVE file")
            else:
                valid_wave = True
            
            iteration = 0
            while True:
                iteration += 1
                chunk_id, chunk_size = struct.unpack('<4sI', file.read(8))

                if chunk_id == b'JUNK':
                    header_size += 8 + chunk_size
                    file.read(chunk_size)
                    continue

                if chunk_id == b'fmt ':
                    header_size += 8 + chunk_size
                    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', file.read(chunk_size))
                    continue

                if chunk_id == b'data':
                    header_size += 8
                    break

                if iteration > 100:
                    header_size = 44
                    break
        

        num_channels_var.set(num_channels)
        sample_rate_var.set(sample_rate)
        bits_per_sample_var.set(bits_per_sample)
        set_duration()
        result_label.config(text=f"WAV header detected")

    except Exception as e:
        header_size = 44
        num_channels_var.set('')
        sample_rate_var.set('')
        bits_per_sample_var.set('')
        result_label.config(text=f"Could not read header.\n{e}")


def update_wav_header():
    global header_size, valid_wave

    try:
        if valid_wave == False and forceheader_var.get() == 0:
            raise ValueError("Not a valid WAVE file")
    
        input_file_path = input_file_path_entry.get()

        header_size = 44
        num_channels = int(num_channels_var.get())
        sample_rate = int(sample_rate_var.get())
        bits_per_sample = int(bits_per_sample_var.get())
        file_size = os.path.getsize(input_file_path)
        data_size = file_size - header_size

        with open(input_file_path, 'r+b') as file:
            # header size is usually 44 or 80. If not, first couple ms will be junk. Aimed for maximum compatibility 
            if header_size == 80:
                new_header = struct.pack(
                    '<4sI4s4sIIIIIIII4sIHHIIHH4sI',
                    b'RIFF',        # 4s
                    file_size - 8,  # I
                    b'WAVE',        # 4s
                    b'JUNK',        # 4s
                    28,             # I
                    0, 0, 0, 0, 0, 0, 0, # IIIIIII - empty JUNK header
                    b'fmt ',        # 4s
                    16,             # I
                    1,              # H
                    num_channels,   # H
                    sample_rate,    # I
                    sample_rate * num_channels * bits_per_sample // 8, # I  - byte rate
                    num_channels * bits_per_sample // 8, # H - block align (number of bytes for one sample, including all channels)
                    bits_per_sample,# H
                    b'data',        # 4s
                    data_size       # I
                )
            else:
                new_header = struct.pack(
                    '<4sI4s4sIHHIIHH4sI',
                    b'RIFF',        # 4s
                    file_size - 8,  # I
                    b'WAVE',        # 4s
                    b'fmt ',        # 4s
                    16,             # I
                    1,              # H
                    num_channels,   # H
                    sample_rate,    # I
                    sample_rate * num_channels * bits_per_sample // 8, # I  - byte rate
                    num_channels * bits_per_sample // 8, # H - block align (number of bytes for one sample, including all channels)
                    bits_per_sample,# H
                    b'data',        # 4s
                    data_size       # I
                )
            
            file.seek(0)
            file.write(new_header)
            result_label.config(text=f"The header was updated with the given information.\n{input_file_path}")
    except Exception as e:
        result_label.config(text=f"Could not update header:\n{e}")

def set_duration():
    input_file_path = input_file_path_entry.get()
    file_size = os.path.getsize(input_file_path)
    num_channels = int(num_channels_var.get())
    sample_rate = int(sample_rate_var.get())
    bits_per_sample = int(bits_per_sample_var.get())
    data_size = file_size - header_size
    sample_size = bits_per_sample // 8
    num_samples = data_size // (num_channels * sample_size)
    duration_seconds = int(num_samples / sample_rate)
    duration_seconds_var.set(duration_seconds)

def toggle_combobox_state():
    state = str(num_channels_dropdown.cget("state"))
    if state == 'normal':
        num_channels_dropdown.config(state="disabled")
        sample_rate_dropdown.config(state="disabled")
        bits_per_sample_dropdown.config(state="disabled")
    else:
        num_channels_dropdown.config(state="normal")
        sample_rate_dropdown.config(state="normal")
        bits_per_sample_dropdown.config(state="normal")

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
input_file_path_entry = ttk.Entry(frame, width=50)
input_file_path_entry.grid(row=1, column=0, columnspan=2)
ttk.Button(frame, text="Browse", command=lambda: get_spec()).grid(row=0, column=2, rowspan=2)

ttk.Label(frame, text="Number of Channels:").grid(row=2, column=0, sticky="w")
num_channels_var = tk.StringVar()
num_channels_dropdown = ttk.Combobox(frame, textvariable=num_channels_var, values=[1, 2, 8], font=custom_font, state="disabled")
num_channels_dropdown.grid(row=2, column=1)

ttk.Label(frame, text="Sample Rate:").grid(row=3, column=0, sticky="w")
sample_rate_var = tk.StringVar()
sample_rate_dropdown = ttk.Combobox(frame, textvariable=sample_rate_var, values=[44100, 48000, 96000], font=custom_font, state="disabled")
sample_rate_dropdown.grid(row=3, column=1)

ttk.Label(frame, text="Bit Depth:").grid(row=4, column=0, sticky="w")
bits_per_sample_var = tk.StringVar()
bits_per_sample_dropdown = ttk.Combobox(frame, textvariable=bits_per_sample_var, values=[16, 24, 32], font=custom_font, state="disabled")
bits_per_sample_dropdown.grid(row=4, column=1)

ttk.Label(frame, text="Time:").grid(row=5, column=0, sticky="w")
duration_seconds_var = tk.StringVar()
duration_seconds_label = ttk.Label(frame, textvariable=duration_seconds_var, font=custom_font)
duration_seconds_label.grid(row=5, column=1)

durationcalc_button = ttk.Button(frame, text="calculate time", command=set_duration)
durationcalc_button.grid(row=5, column=2)

forceheader_var = tk.IntVar()
forceheader_checkbox = ttk.Checkbutton(frame, text="force header", variable=forceheader_var)
forceheader_checkbox.grid(row=6, column=0)

manualsettings_var = tk.IntVar()
manualsettings_checkbox = ttk.Checkbutton(frame, text="manual setting", variable=manualsettings_var, command=toggle_combobox_state)
manualsettings_checkbox.grid(row=6, column=1)

update_button = ttk.Button(frame, text="Update Header", command=update_wav_header)
update_button.grid(row=6, column=2)

result_label = ttk.Label(frame, text="")
result_label.grid(row=7, columnspan=3)

root.mainloop()
