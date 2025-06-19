
# easyYt

**easyYt** is a lightweight YouTube downloader built with Python, GTK4, and yt-dlp.  
It supports downloading videos, music, and playlists in multiple formats via a simple GUI.

---

## Requirements

- Python 3
- PyGObject with GTK4 support
- yt-dlp
- ffmpeg (required by yt-dlp for audio format conversion)

---

## Installing Dependencies

### Debian / Ubuntu

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 yt-dlp ffmpeg
```

### Arch Linux

```bash
sudo pacman -S python-gobject gtk4 yt-dlp ffmpeg
```

### Fedora

```bash
sudo dnf install python3-gobject gtk4 yt-dlp ffmpeg
```

---


## Installation

1. Clone or download the easyYt project folder.

2. Make the main script executable:

```bash
chmod +x main.py
````

3. (Optional) Move the main script to a directory in your PATH (e.g., `~/.local/bin`) and rename it to `easyyt`:

```bash
mv main.py ~/.local/bin/easyyt
```

Make sure `~/.local/bin` is in your PATH (this is usually the case).

4. Run the app once to automatically generate the desktop entry (`easyyt.desktop`) in `~/.local/share/applications/`.

```bash
easyyt
```

This will create a `.desktop` file so easyYt appears in your application menu.



---

## Running easyYt

You can start the app by running:

```bash
easyyt
```

Or launch it from your desktop environment's application menu.

---

## Packaging (optional)

To create a standalone executable:

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build the executable:

```bash
pyinstaller --name easyyt --onefile --windowed main.py
```

The standalone executable will be located in the `dist` directory.