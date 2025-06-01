import os
import math
import struct
import gzip
import binascii
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk
from tkinter import Button, Label
from tkinter import messagebox
import xml.etree.ElementTree as ET
import subprocess
import shutil

def pack_character_to_font(font_file_path):
    print("Start create font file")
    folder_path = 'fonts'
    file_names = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.tga'):
            file_names.append(filename)

    header = "544E4F4628000000280000000400000018000000"
    with open(font_file_path, "wb") as file:
        binary_data = bytes.fromhex(header)
        file.write(binary_data)
        file.write(struct.pack("<i", len(file_names)))
        offsets=len(file_names)*8+24
        offset=offsets
        all_size=0
        for filename in file_names:
            parts = filename.split('_')
            number, char, k_left, k_top, k_right_with_extension = parts
            k_right = os.path.splitext(k_right_with_extension)[0]
            file.write(struct.pack("<i", int(char)))
            file.write(struct.pack("<i", offset))

            with open("fonts/"+filename, 'rb') as char_image_file:
                char_image_file.seek(12)
                width = struct.unpack("<H", char_image_file.read(2))[0]
                height = struct.unpack("<H", char_image_file.read(2))[0]
                char_image_file.seek(18)
                image_data = char_image_file.read(width * height * 4)
                size=width * height
                all_size += size+5
                offset=offsets+all_size

        for filename in file_names:
            parts = filename.split('_')
            number, char, k_left, k_top, k_right_with_extension = parts
            k_left = int(k_left)
            k_top = int(k_top)
            k_right = int(os.path.splitext(k_right_with_extension)[0])
            print(f'Number={number}, Char={chr(int(char))}, Kerning left={k_left}, Kerning top={k_top}, Kerning right={k_right}')
            with open("fonts/"+filename, 'rb') as char_image_file:
                char_image_file.seek(12)
                width = struct.unpack("<H", char_image_file.read(2))[0]
                height = struct.unpack("<H", char_image_file.read(2))[0]
                char_image_file.seek(18)
                image_data = char_image_file.read(width * height * 4)
                file.write(struct.pack('B', width))
                file.write(struct.pack('B', height))
                file.write(struct.pack('B', k_left))    # kerning from left
                file.write(struct.pack('B', k_top))     # kerning from top
                file.write(struct.pack('B', k_right))   # kerning from right
                for i in range(width * height):
                    alpha = image_data[i*4 + 3]
                    file.write(struct.pack('B', alpha))

def main(font_file_path):
    pack_character_to_font(font_file_path)

def main_ex(font_file_path):
    os.system("cls")
    f = open(font_file_path, 'rb')
    if not os.path.exists("fonts"):
        os.makedirs("fonts")
    magic		= struct.unpack("L", f.read(4))[0]
    unk0		= struct.unpack("L", f.read(4))[0]
    unk1		= struct.unpack("L", f.read(4))[0]
    unk2		= struct.unpack("L", f.read(4))[0]
    unk3		= struct.unpack("L", f.read(4))[0]
    charsCount	= struct.unpack("L", f.read(4))[0]

    for h in range(charsCount):
        f.seek(24 + h * 8)
        char	= struct.unpack("L", f.read(4))[0]
        offset	= struct.unpack("L", f.read(4))[0]

        f.seek(offset)
        width	= struct.unpack("B", f.read(1))[0]
        height	= struct.unpack("B", f.read(1))[0]
        k_left	= struct.unpack("B", f.read(1))[0] # kerning from left
        k_top	= struct.unpack("B", f.read(1))[0] # kerning from top
        k_right	= struct.unpack("B", f.read(1))[0] # kerning from right
        #f.read(3)

        save	= open("fonts/"+str(h).zfill(6)+"_"+str(char)+"_"+str(k_left)+"_"+str(k_top)+"_"+str(k_right)+".tga","wb")
        save.write(struct.pack('B', 0))
        save.write(struct.pack('B', 0))			# is mapped?
        save.write(struct.pack('B', 2))			# 
        save.write(struct.pack('H', 0))			# first color index
        save.write(struct.pack('H', 0))			# number of colors
        save.write(struct.pack('B', 32))		# bits per color
        save.write(struct.pack('H', 0))			# x-origin
        save.write(struct.pack('H', 0))			# y-origin
        save.write(struct.pack('H', width))	    # width
        save.write(struct.pack('H', height))	# height
        save.write(struct.pack('B', 32))		# bits per pixel
        save.write(struct.pack('B', 32))
    
        for i in range(width*height):
            save.write(struct.pack('B', 0))
            save.write(struct.pack('B', 0))
            save.write(struct.pack('B', 0))
            save.write(f.read(1))

def open_font_file():
    font_file_path = filedialog.askopenfilename(title="Open Font File", filetypes=[("Raw files", "*.raw")])
    if font_file_path:
        try:
            print(f"Font file selected: {font_file_path}")
            main(font_file_path)
            messagebox.showinfo("Success", "Characters packed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"An error occurred: {e}")

def open_font_file_ex():
    font_file_path = filedialog.askopenfilename(title="Open Font File", filetypes=[("Raw files", "*.raw")])
    if font_file_path:
        try:
            print(f"Font file selected: {font_file_path}")
            main_ex(font_file_path)
            messagebox.showinfo("Success", "Characters extract successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"An error occurred: {e}")

def extract_gzip_from_file(file_path, output_file_path, start_position, gzip_size):
    try:
        with open(file_path, 'rb') as file:
            file.seek(start_position)
            gzip_data = file.read(gzip_size)
        with open(output_file_path, 'wb') as output_file:
            output_file.write(gzip_data)
    except Exception as e:
        messagebox.showerror("Failed", f"Error during extraction:\n{e}")
        print(f"Error during extraction: {e}")
        
def find_7z_executable():
    # Common 7-Zip installation paths
    possible_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        os.path.join(os.getenv('APPDATA'), 'Local\\Programs\\7-Zip\\7z.exe')
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Try searching PATH
    if shutil.which("7z"):
        return "7z"

    return None

def decompress_with_7z(gz_file_path):
    seven_zip = find_7z_executable()
    if not seven_zip:
        messagebox.showerror("7-Zip Not Found", "7-Zip is not installed or not in system PATH.")
        return False

    output_dir = os.path.dirname(gz_file_path) or "."  # Use current dir if empty

    try:
        result = subprocess.run(
            [seven_zip, "x", gz_file_path, f"-o{output_dir}", "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        print("7-Zip Output:\n", result.stdout)
        messagebox.showinfo("Success", f"{gz_file_path} successfully decompressed.\n 7-Zip Results:\n\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print("7-Zip Error:\n", e.stderr)
        messagebox.showwarning("Decompressed", f"{gz_file_path} appears to be modded before, check the file carefully before modding.\n\n7-Zip Results:\n\n{e.stderr}")
        return False

def compress_with_7z(raw_file_path, gz_file_path):
    seven_zip = find_7z_executable()
    if not seven_zip:
        messagebox.showerror("7-Zip Not Found", "7-Zip is not installed or not in system PATH.")
        return False

    try:
        result = subprocess.run(
            [seven_zip, "a", "-tgzip", "-mx9", gz_file_path, raw_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        print("7-Zip Compression Output:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("7-Zip Compression Error:\n", e.stderr)
        messagebox.showerror("Compression Failed", f"7-Zip failed to compress {raw_file_path}\n\nError:\n{e.stderr}")
        return False

def run_extractmgs2_gzip():
    extract_gzip_from_file('METAL GEAR SOLID2.exe', 'MGS_Font_nht.raw.gz', 8725008, 969470)
    if os.path.exists("MGS_Font_nht.raw.gz"):
        decompress_with_7z("MGS_Font_nht.raw.gz")

def run_extractmgs3_gzip():
    extract_gzip_from_file('METAL GEAR SOLID3.exe', 'MGS_Font_nht.raw.gz', 10283248, 983133)
    if os.path.exists("MGS_Font_nht.raw.gz"):
        decompress_with_7z("MGS_Font_nht.raw.gz")
    
def run_extractmanual_gzip():
    file_path = filedialog.askopenfilename(title="Select Binary File (e.g., .exe)", filetypes=[("All Files", "*.*")])
    if not file_path:
        return

    start_pos = simpledialog.askinteger("Start Position", "Enter start byte position:")
    gzip_size = simpledialog.askinteger("GZIP Size", "Enter number of bytes to extract:")

    if start_pos is None or gzip_size is None:
        return

    output_file_path = filedialog.asksaveasfilename(defaultextension=".gz", filetypes=[("GZIP Files", "*.gz")])
    if not output_file_path:
        return

    extract_gzip_from_file(file_path, output_file_path, start_pos, gzip_size)

def overwrite_gzip_to_file(file_path, input_file_path, start_position, gzip_size):
    try:
        # Read the content to be inserted from the 'MGS_Font_nht.raw' file.
        with open(input_file_path, 'rb') as input_file:
            decompressed_data = input_file.read()

        with open(file_path, 'r+b') as file:
            # Move to the beginning of the Gzip file.
            file.seek(start_position)
            # Write the decompressed data to the specified position.
            file.write(decompressed_data)

        print(f"Overwritten content from '{input_file_path}' to '{file_path}'.")
        messagebox.showinfo("Success", f"MGS_Font_nht.raw.gz has been imported into\n'{file_path}'")
    except Exception as e:
        print(f"Error during overwrite: {e}")
        messagebox.showerror("Failed", f"Error during import:\n{e}")
        
def run_importmgs2_gzip():
    raw_path = "MGS_Font_nht.raw"
    gz_path = "MGS_Font_nht.raw.gz"

    if not os.path.exists(raw_path):
        messagebox.showerror("File Not Found", f"{raw_path} not found. Cannot compress.")
        return

    if compress_with_7z(raw_path, gz_path):
        overwrite_gzip_to_file('METAL GEAR SOLID2.exe', gz_path, 8725008, 969470)

def run_importmgs3_gzip():
    raw_path = "MGS_Font_nht.raw"
    gz_path = "MGS_Font_nht.raw.gz"

    if not os.path.exists(raw_path):
        messagebox.showerror("File Not Found", f"{raw_path} not found. Cannot compress.")
        return

    if compress_with_7z(raw_path, gz_path):
        overwrite_gzip_to_file('METAL GEAR SOLID3.exe', gz_path, 10283248, 983133)


# --- GUI Setup ---
root = tk.Tk()
root.title("MGSHD Font Packer (RAW font proccessing from GIZA)")
root.geometry("500x450")

# --- Frames for Grouping Buttons ---
extract_mgs_frame = tk.LabelFrame(root, text="Extract MGS Fonts", padx=10, pady=10)
extract_mgs_frame.pack(padx=10, pady=5, fill="both")

pack_unpack_frame = tk.LabelFrame(root, text="Pack/Unpack Font", padx=10, pady=10)
pack_unpack_frame.pack(padx=10, pady=5, fill="both")

import_mgs_frame = tk.LabelFrame(root, text="Import MGS Fonts", padx=10, pady=10)
import_mgs_frame.pack(padx=10, pady=5, fill="both")

manual_frame = tk.LabelFrame(root, text="Manual Tools", padx=10, pady=10)
manual_frame.pack(padx=10, pady=5, fill="both")

# --- Status Bar ---
status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# --- Button Functions with Status Updates ---

def set_status(message):
    status_bar.config(text=message)

# Helper to create buttons with hover effect
def create_button(parent, text, command):
    btn = tk.Button(parent, text=text, command=command)
    btn.pack(pady=5, anchor='w')
    btn.bind("<Enter>", lambda e: set_status(f"Hovering: {text}"))
    btn.bind("<Leave>", lambda e: set_status("Ready"))
    return btn

# --- Extract MGS Fonts Buttons ---
create_button(extract_mgs_frame, "Extract MGS2 Font From METAL GEAR SOLID2.exe", run_extractmgs2_gzip)
create_button(extract_mgs_frame, "Extract MGS3 Font From METAL GEAR SOLID3.exe", run_extractmgs3_gzip)

# --- Import MGS Fonts Buttons ---
create_button(import_mgs_frame, "Import MGS_Font_nht.raw.gz into METAL GEAR SOLID2.exe", run_importmgs2_gzip)
create_button(import_mgs_frame, "Import MGS_Font_nht.raw.gz into METAL GEAR SOLID3.exe", run_importmgs3_gzip)

# --- Manual Tools Buttons ---
create_button(manual_frame, "Manually Extract Font From *.exe", run_extractmanual_gzip)

# --- Pack/Unpack Buttons ---
create_button(pack_unpack_frame, "Extract *.Raw font contents", open_font_file_ex)
create_button(pack_unpack_frame, "Pack *.Raw font contents", open_font_file)

# --- Run GUI Loop ---
root.mainloop()