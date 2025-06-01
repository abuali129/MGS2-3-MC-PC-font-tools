import os
from tkinter import messagebox, Checkbutton
from tkinter import Tk, Label, Button, Entry, Spinbox, filedialog, StringVar, IntVar, Text, END, Scrollbar, Frame
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import xml.etree.ElementTree as ET
import glob

def escape_xml_char(char):
    if char == '"':
        return "&quot;"
    elif char == '&':
        return "&amp;"
    elif char == '<':
        return "&lt;"
    elif char == '>':
        return "&gt;"
    elif char == "'":
        return "&apos;"
    return char

def write_custom_tga(image, output_path):
    width, height = image.size
    pixel_data = image.tobytes()
    header = bytearray([
        0x00,      
        0x00,      
        0x02,      
        0x00, 0x00,
        0x00, 0x00,
        0x20,      
        0x00, 0x00,
        0x00, 0x00,
        width & 0xFF, (width >> 8) & 0xFF,
        height & 0xFF, (height >> 8) & 0xFF,
        0x20,
        0x20
    ])
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(pixel_data)

def parse_character_ranges(input_string):
    ranges = []
    parts = [part.strip() for part in input_string.split(",")]
    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            ranges.append((int(start), int(end)))
        else:
            code = int(part)
            ranges.append((code, code))
    return ranges

    log_text.insert(END, "Starting conversion...\n")

def ttf_to_tga_with_xml(ttf_path, font_size, char_ranges, log_text):
    log_text.insert(END, "Starting conversion...\n")
    font = TTFont(ttf_path)
    cmap = font['cmap']
    t = cmap.getBestCmap()
    pil_font = ImageFont.truetype(ttf_path, size=font_size)
    
    # Get font metrics for vertical alignment
    ascent, descent = pil_font.getmetrics()
    line_height = ascent + descent

    root = ET.Element("Characters")

    if not char_ranges:
        char_ranges = [(min(t.keys()), max(t.keys()))]

    # Output directory
    output_dir = os.path.join(os.path.dirname(ttf_path), "fonts")
    os.makedirs(output_dir, exist_ok=True)

    # Retrieve UI variables
    harakat_zero_spacing = harakat_spacing_var.get()
    isolated_spacing_adj = isolated_spacing_var.get()
    initial_spacing_adj = initial_spacing_var.get()
    y_offset_adj = y_offset_var.get()
    generate_xml = generate_xml_var.get()

    # Predefined character sets
    HARAKAT_CHARS = {
        1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619,
        65136, 65138, 65140, 65142, 65144, 65146, 65148, 65150
    }
    ISOLATED_CHARS = {
        1548, 1563, 65152, 65153, 65155, 65157, 65159, 65161, 65165,
        65167, 65171, 65173, 65177, 65181, 65185, 65189, 65193, 65195,
        65197, 65199, 65201, 65205, 65209, 65213, 65217, 65221, 65225,
        65229, 65233, 65237, 65241, 65245, 65249, 65253, 65257, 65261,
        65263, 65265, 65269, 65271, 65273, 65275
    }
    INITIAL_CHARS = {
        65163, 65169, 65175, 65179, 65183, 65187, 65191, 65203, 65207,
        65211, 65215, 65219, 65223, 65227, 65231, 65235, 65239, 65243,
        65247, 65251, 65255, 65259, 65267
    }

    file_index = 158  # Start index for filenames

    for start, end in char_ranges:
        for char_code in range(start, end + 1):
            if char_code not in t:
                continue
            try:
                char = chr(char_code)
                escaped_char = escape_xml_char(char)

                img = Image.new("RGBA", (512, 512), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(img)

                # Draw text at (0, 0)
                draw.text((0, 0), char, font=pil_font, fill=(0, 0, 0, 255))
                bbox = img.getbbox()

                if bbox:
                    cropped_img = img.crop(bbox)

                    # Calculate dimensions and offsets
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    x_offset = bbox[0]
                    y_offset = line_height - (ascent - bbox[1])

                    # Apply y_offset adjustment
                    y_offset += y_offset_adj
                    y_offset = max(0, y_offset)

                    # Apply spacing logic
                    if char_code in HARAKAT_CHARS and harakat_zero_spacing:
                        spacing = 0
                    elif char_code in ISOLATED_CHARS:
                        spacing = max(0, width + isolated_spacing_adj)
                    elif char_code in INITIAL_CHARS:
                        spacing = max(0, width + initial_spacing_adj)
                    else:
                        spacing = max(0, width + default_spacing_var.get())

                    # Generate custom filename
                    filename = f"{file_index:06d}_{char_code}_{x_offset}_{y_offset}_{spacing}.tga"
                    output_path = os.path.join(output_dir, filename)

                    # Delete existing files with the same serial number
                    pattern = os.path.join(output_dir, f"{file_index:06d}_*.tga")
                    for old_file in glob.glob(pattern):
                        try:
                            os.remove(old_file)
                            log_text.insert(END, f"Deleted old file: {old_file}\n")
                        except Exception as e:
                            log_text.insert(END, f"Failed to delete {old_file}: {e}\n")

                    # Write new TGA file
                    write_custom_tga(cropped_img, output_path)

                    # Add character data to XML
                    if generate_xml:
                        char_element = ET.SubElement(root, "Character", {
                            "code": str(char_code),
                            "char": escaped_char,
                            "width": str(width),
                            "height": str(height),
                            "x_offset": str(x_offset),
                            "y_offset": str(y_offset),
                            "spacing": str(spacing)
                        })

                    log_text.insert(END, f"Generated {output_path} with width={width}, height={height}, x_offset={x_offset}, y_offset={y_offset}, spacing={spacing}\n")
                    file_index += 1
            except Exception as e:
                log_text.insert(END, f"Failed to process character {char_code}: {e}\n")

    # Write XML metadata (only if checkbox is selected)
    if generate_xml:
        xml_path = os.path.join(os.path.dirname(ttf_path), "characters.xml")
        with open(xml_path, "w", encoding="utf-8") as xml_file:
            xml_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            xml_file.write("<Characters>\n")
            for char_element in root.findall("Character"):
                attrs = ' '.join([f'{k}="{v}"' for k, v in char_element.attrib.items()])
                xml_file.write(f"  <Character {attrs} />\n")
            xml_file.write("</Characters>")
        log_text.insert(END, f"XML file saved at {xml_path}\n")

    log_text.see(END)
    messagebox.showinfo("Conversion Complete", "The TTF to TGA conversion process is complete!")

def select_ttf_file():
    file_path = filedialog.askopenfilename(filetypes=[("TTF Files", "*.ttf")])
    if file_path:
        ttf_file_var.set(file_path)

def start_conversion(log_text):
    ttf_path = ttf_file_var.get()
    font_size = font_size_var.get()
    char_ranges_input = char_ranges_var.get()
    if not ttf_path:
        log_text.insert(END, "Please select a TTF file.\n")
        log_text.see(END)
        return
    try:
        if char_ranges_input.strip():
            char_ranges = parse_character_ranges(char_ranges_input)
        else:
            char_ranges = None
    except Exception as e:
        log_text.insert(END, f"Invalid character ranges format: {e}\n")
        log_text.see(END)
        return
    ttf_to_tga_with_xml(ttf_path, font_size, char_ranges, log_text)

root = Tk()
root.title("GIZA compatible TTF to TGA Converter for MGSHD Collection")
generate_xml_var = IntVar(value=0)  # Default: don't generate XML
ttf_file_var = StringVar()
font_size_var = IntVar(value=45)
char_ranges_var = StringVar(value="1548, 1563, 1567, 1600, 1611-1619, 65152-65276")
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(1, weight=1)
Label(root, text="TTF File:").grid(row=0, column=0, sticky="w")
Entry(root, textvariable=ttf_file_var, width=50).grid(row=0, column=1, sticky="ew")
Button(root, text="Browse", command=select_ttf_file).grid(row=0, column=2, sticky="ew")
Label(root, text="Font Size:").grid(row=1, column=0, sticky="w")
Spinbox(
    root,
    from_=8,
    to=300,
    increment=1,
    textvariable=font_size_var,
    width=10
).grid(row=1, column=1, sticky="w")
Label(root, text="Character Ranges (e.g., 1548, 1563, 1567, 1600, 1611-1619, 65152-65276):").grid(row=2, column=0, sticky="w")
Entry(root, textvariable=char_ranges_var, width=50).grid(row=2, column=1, sticky="ew")
# Additional UI elements for spacing/y_offset adjustments
default_spacing_var = IntVar(value=0)
Label(root, text="Default Spacing Adjustment (+/-):").grid(row=5, column=0, sticky="w")
Spinbox(root, from_=-50, to=50, increment=1, textvariable=default_spacing_var, width=10).grid(
    row=5, column=1, sticky="w")
isolated_spacing_var = IntVar(value=0)
Label(root, text="Isolated Spacing Adjustment (+/-):").grid(row=6, column=0, sticky="w")
Spinbox(root, from_=-50, to=50, increment=1, textvariable=isolated_spacing_var, width=10).grid(
    row=6, column=1, sticky="w")

initial_spacing_var = IntVar(value=0)
Label(root, text="Initial Spacing Adjustment (+/-):").grid(row=7, column=0, sticky="w")
Spinbox(root, from_=-50, to=50, increment=1, textvariable=initial_spacing_var, width=10).grid(
    row=7, column=1, sticky="w")

y_offset_var = IntVar(value=0)
Label(root, text="Global Y Offset Adjustment (+/-):").grid(row=8, column=0, sticky="w")
Spinbox(root, from_=-50, to=50, increment=1, textvariable=y_offset_var, width=10).grid(
    row=8, column=1, sticky="w")
harakat_spacing_var = IntVar(value=1)
Checkbutton(root, text="Force spacing to 0 for Harakat", variable=harakat_spacing_var).grid(
    row=9, column=0, columnspan=3, sticky="w")
# XML Toggle Checkbox
Checkbutton(root, text="Generate characters.xml", variable=generate_xml_var).grid(
    row=10, column=0, columnspan=3, sticky="w")

Button(
    root,
    text="Start Conversion",
    command=lambda: start_conversion(log_text),
    bg="green",
    fg="white",
    activebackground="darkgreen",
    activeforeground="white"
).grid(row=3, column=0, columnspan=3, sticky="n")
log_frame = Frame(root)
log_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
log_frame.grid_rowconfigure(0, weight=1)
log_frame.grid_columnconfigure(0, weight=1)
scrollbar = Scrollbar(log_frame)
scrollbar.grid(row=0, column=1, sticky="ns")
log_text = Text(log_frame, height=10, width=80, yscrollcommand=scrollbar.set, wrap="word")
log_text.grid(row=0, column=0, sticky="nsew")
scrollbar.config(command=log_text.yview)
root.mainloop()