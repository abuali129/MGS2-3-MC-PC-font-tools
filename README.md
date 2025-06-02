# MGS2 & 3 Font Tools for RAW Font Modding  
## (RAW Font Packer + TTF-to-TGA Converter)

This guide and toolchain allows you to **extract, modify, generate, repack, and re-import** RAW font files used in the *Metal Gear Solid HD Collection* games (MGS2 and MGS3). It combines two tools:

- **RAW Font Packer Tool** – For unpacking and repacking RAW fonts
- **TTF-to-TGA Converter Tool** – For generating new glyphs from a `.ttf` font

Both tools share the same `fonts/` folder by default, which is crucial to understand when combining old and new glyph sets.

---

## 🧰 Required Libraries

Make sure these are installed before running the tools:

```bash
pip install tkinter pillow fonttools
```

Also required:
- **7-Zip (`7z.exe`)** – Used for GZIP compression/decompression  
  - [Download 7-Zip](https://www.7-zip.org/)
  - Ensure it is added to your system PATH or located in `C:\Program Files\7-Zip`

---

## 📁 Folder Structure Overview

Place both scripts in the same working directory:

```
working_folder/
├── fonts/              # Shared folder used by both tools
│   ├── 000001_1563_2_0_3.tga
│   └── ...
├── MGS_Font_nht.raw    # Font file extracted from EXE
├── MGS_Font_nht.raw.gz # Compressed version of RAW font
├── METAL GEAR SOLID2.exe / METAL GEAR SOLID3.exe
├── font_packer.py      # RAW Font Packer (unpack/pack)
└── ttf_to_tga_gui.py   # TTF-to-TGA converter
```

> ✅ Both tools use the `fonts/` folder by default to store `.tga` glyph images.

---

## 🔁 Full Font Modding Workflow with Both Tools

### 1️⃣ Extract RAW Font From Game EXE

- Run `font_packer.py`
- Click:
  - `Extract MGS2 Font From METAL GEAR SOLID2.exe`  
    OR  
  - `Extract MGS3 Font From METAL GEAR SOLID3.exe`
- This will extract and decompress the RAW font as:
  ```
  MGS_Font_nht.raw
  ```

---

### 2️⃣ Unpack RAW Font Into Glyphs

- In the same tool, click:
  - `Extract *.Raw font contents`
- Select `MGS_Font_nht.raw`
- The tool will unpack all characters into:
  ```
  fonts/000000_*.tga
  ```

✅ These are now ready for editing or replacement.

---

### 3️⃣ Generate New Glyphs Using TTF-to-TGA Converter

#### 🛠️ Step-by-step:

1. **Run the TTF-to-TGA GUI** (`ttf_to_tga_gui.py`)
2. **Select your `.ttf` font file**
3. **Set desired character ranges** (e.g., Arabic, special symbols)  
   👉 You can find Unicode range references here:  
   🔗 [Unicode Blocks and Ranges Reference (Arabic Included)](https://www.unicode.org/charts/nameslist/index.html)

   Example input:
   ```
   1536-1791       ← Arabic block
   64256-64335     ← Arabic Supplemental Forms
   65152-65276     ← Arabic Presentation Forms-B
   ```

4. **Adjust spacing/y-offset if needed**
5. Click `Start Conversion`

🔄 The tool will:
- Delete any existing `.tga` files in `fonts/` that match the same serial index
- Generate new `.tga` files starting at index `000158`:
  ```
  fonts/000158_charcode_xoff_yoff_spacing.tga
  ```

> ⚠️ **Important**: Because both tools write to the same `fonts/` folder, running the TTF-to-TGA converter will overwrite previously extracted glyphs unless you rename or move them.

---

### 4️⃣ Repack Modified Glyphs Into RAW Font

- Go back to the **RAW Font Packer GUI**
- Click: `Pack *.Raw font contents`
- Select the original `MGS_Font_nht.raw`

🔄 The tool will:
- Read all `.tga` files in `fonts/`
- Rebuild the RAW font using the latest glyphs
- Overwrite `MGS_Font_nht.raw`

✅ Now your font includes both old and newly generated glyphs!

---

### 5️⃣ Import Updated Font Back Into Game EXE

- In the RAW Font Packer GUI:
  - For MGS2: click `Import MGS_Font_nht.raw.gz into METAL GEAR SOLID2.exe`
  - For MGS3: click `Import MGS_Font_nht.raw.gz into METAL GEAR SOLID3.exe`

🔄 The tool will:
- Compress the updated `MGS_Font_nht.raw` into a `.gz`
- Replace the embedded font section inside the game executable

---

## 🧠 Important Notes About Character Indexing

### 🔄 Integration Tips

- Index is starting from 158 to avoid replacing original English characters.
- To change the starting index in `ttf_to_tga_gui.py`,
  ```python
  file_index = 158  
  ```
There's enough room to create any character set by replacing Japanese ones. 
However, download xnview to review the glyphs before and after your mod.
---

## 💡 Special Notes on Harakat & Initial Forms (Arabic Specific)

The following options in the TTF-to-TGA tool are specifically designed for **Arabic ligatures and diacritics**:

- **"Force spacing to 0 for Harakat"**  
  Applies to marks like Fatha, Damma, Sukoon, etc.  
  Only affects these specific character codes:
  ```python
  HARAKAT_CHARS = {
      1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619,
      65136, 65138, 65140, 65142, 65144, 65146, 65148, 65150
  }
  ```

- **Isolated / Initial Forms Spacing Adjustments**  
  Helps render Arabic letters correctly depending on their position in a word.  
  These apply only to:
  ```python
  ISOLATED_CHARS = { ... }  # Characters that appear alone
  INITIAL_CHARS = { ... }    # Characters at the start of a word
  ```

> ⚠️ These settings only work for the above-defined ranges. If you're targeting other languages or scripts, you may need to **manually edit these sets** in the code to fit your needs for special y offset editing or remove force x offset to 0 to some characters if needed.

---

## 💡 Best Practices

- Always **backup your `fonts/` folder** before running either tool.
- Use unique **character ranges** in the TTF tool to only generate what’s needed.
- Consider writing a small script to **rename/reindex `.tga` files** if needed.
- Test the final font in-game to verify alignment and display order.

---

## ✅ Final Notes

By placing both scripts in the same directory and using the shared `fonts/` folder, you can seamlessly:

- Extract → Unpack → Generate new glyphs → Repack → Re-import

This makes modding games font much easier and more flexible to add your language support to the game.

---

## 🧑‍💻 Developer Credits

Tools originally by GIZA developed for the *Metal Gear Solid HD Collection* modding community.
