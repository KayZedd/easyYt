#!/usr/bin/env python3
import gi
import subprocess
import threading
from pathlib import Path
import re
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio

from gi.repository import GdkPixbuf
from pathlib import Path

def create_desktop_file():
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = desktop_dir / "easyyt.desktop"
    script_path = Path(__file__).resolve()
    icon_path = Path(__file__).parent / "assets" / "easyyt.png"
    exec_cmd = f"python3 {script_path}"

    desktop_content = f"""[Desktop Entry]
Name=easyYt
Comment=Lightweight YouTube downloader using yt-dlp and GTK4
Exec={exec_cmd}
Icon={str(icon_path.resolve())}
Terminal=false
Type=Application
Categories=AudioVideo;Network;
StartupNotify=true
"""

    if not desktop_file.exists():
        with open(desktop_file, "w") as f:
            f.write(desktop_content)
        print(f"Created desktop entry at {desktop_file}")
    else:
        print(f"Desktop entry already exists at {desktop_file}")

class EasyYtWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("easyYt")
        self.set_default_size(400, 250)

        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.set_titlebar(header)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        self.set_child(box)

        self.url_entry = Gtk.Entry(placeholder_text="YouTube URL…", hexpand=True)
        box.append(self.url_entry)

        self.format_dropdown = Gtk.DropDown.new_from_strings(["MP3", "MP4", "FLAC"])
        box.append(self.format_dropdown)

        self.folder_button = Gtk.Button(label="Choose Folder…")
        self.folder_button.connect("clicked", self.on_folder_choose)
        box.append(self.folder_button)

        self.output_dir = str(Path.home() / "Downloads")
        self.folder_button.set_label(self.shorten_path(self.output_dir))

        self.download_button = Gtk.Button(label="Download", hexpand=True)
        self.download_button.connect("clicked", self.on_download)
        box.append(self.download_button)

        self.progress = Gtk.ProgressBar(show_text=True)
        box.append(self.progress)

    def shorten_path(self, path, max_len=30):
        if len(path) <= max_len:
            return path
        part_len = (max_len - 1) // 2
        return path[:part_len] + '…' + path[-part_len:]

    def on_folder_choose(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Choose download folder",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Select", Gtk.ResponseType.ACCEPT)

        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                files = dialog.get_files()
                if files:
                    folder = files[0]
                    self.output_dir = folder.get_path()
                    self.folder_button.set_label(self.shorten_path(self.output_dir))
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def on_download(self, widget):
        url = self.url_entry.get_text().strip()
        if not url:
            self.progress.set_text("Please enter a URL")
            return

        formats = ["mp3", "mp4", "flac"]
        fmt = formats[self.format_dropdown.get_selected()]

        self.progress.set_fraction(0)
        self.progress.set_text("Starting download...")

        def run_download():
            cmd = ["yt-dlp", "-P", self.output_dir, url, "--progress", "--newline"]
            if fmt != "mp4":
                cmd += ["-x", "--audio-format", fmt]
            else:
                cmd += ["-f", "best"]

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                )
                for line in process.stdout:
                    GLib.idle_add(self.parse_output, line.strip())
                process.wait()
                if process.returncode == 0:
                    GLib.idle_add(self.progress.set_fraction, 1.0)
                    GLib.idle_add(self.progress.set_text, "Download complete")
                else:
                    GLib.idle_add(self.progress.set_text, "Download failed")
            except Exception as e:
                GLib.idle_add(self.progress.set_text, f"Error: {e}")

        threading.Thread(target=run_download, daemon=True).start()

    def parse_output(self, line):
        percent_match = re.search(r"(\d{1,3}\.\d)%", line)
        if percent_match:
            frac = float(percent_match.group(1)) / 100.0
            self.progress.set_fraction(frac)
            self.progress.set_text(f"Downloading: {int(frac*100)}%")
        elif line.startswith("[download] Downloading video") or line.startswith("[download]"):
            self.progress.set_text(line)
        elif "Merging formats" in line:
            self.progress.set_text("Merging formats...")
        elif "Deleting original file" in line:
            self.progress.set_text("Cleaning up...")

class EasyYtApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.easyyt.app")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        create_desktop_file()
        win = EasyYtWindow(self)
        win.present()

if __name__ == "__main__":
    app = EasyYtApp()
    app.run()
