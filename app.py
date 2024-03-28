import os
import tkinter as tk
from tkinter import ttk, filedialog, Text
import random
import re
import shlex
import subprocess
import time
from threading import Thread
import svc_ttk
from typing import Literal

def create_spacer(frame, height: int = 10, width: int = 200,
                  side: Literal["left", "right", "top", "bottom"] = "top",
                  anchor: str = "center", fill: str = "x", expand: bool = True) -> None:
    spacer = ttk.Frame(frame, height=height, width=width)


tags_to_remove = ['comment', 'description', 'synopsis', 'Long Description']

class MainApp:

    def __init__(self, master=None):

        self.master = master
        self.output_format_var = tk.BooleanVar(value=True)
        self.quality_var = tk.BooleanVar(value=True)
        self.meta_data_var = tk.BooleanVar(value=True)
        self.album_art_var = tk.BooleanVar(value=False)
        self.append_to_albumartist_var = tk.BooleanVar(value=False)
        self.sacad_var = tk.BooleanVar(value=False)
        self.strip_id3_var = tk.BooleanVar(value=False)
        self.resolution = tk.StringVar(value="1000")


        mainwindow = ttk.Frame(master)
        mainwindow.configure(height=750, width=650)

        # Logo, Header
        self.main_frame = ttk.Frame(master)
        self.main_frame.configure(width=200)
        svc_ttk.set_theme("light")  # Starting with a light theme
        self.img_logo_light = tk.PhotoImage(file="logo_light.png")
        self.img_logo_dark = tk.PhotoImage(file="logo_dark.png")
        self.img_blurb_light = tk.PhotoImage(file="blurb_light.png")
        self.img_blurb_dark = tk.PhotoImage(file="blurb_dark.png")

        # Initialize with light theme images
        self.img_logo = self.img_logo_light
        self.img_blurb = self.img_blurb_light

        self.logo_label = ttk.Label(self.main_frame)
        self.logo_label.configure(image=self.img_logo_light, text='logo_label')  # Start with light theme image
        self.logo_label.pack(anchor="w", padx=17, pady=20, side="left")
        self.blurb_label = ttk.Label(self.main_frame)
        self.blurb_label.configure(image=self.img_blurb_light, text='blurb_label')  # Start with light theme image
        self.blurb_label.pack(anchor="w", pady=20, side="left")

        toggle_theme_btn = ttk.Button(self.main_frame, text='🌜  🔆', command=self.toggle_theme)
        toggle_theme_btn.pack(anchor="n", side="right", padx=20, pady=10)
        self.main_frame.pack(anchor="nw", fill="x", side="top")

        def create_spacer(frame, height: int = 10, width: int = 200,
                          side: Literal["left", "right", "top", "bottom"] = "top",
                          anchor: Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"] = "center",
                          fill: Literal["x", "y", "both"] = "x",
                          expand: bool = True) -> None:
            spacer = ttk.Frame(frame, height=height, width=width)
            spacer.pack(side=side, anchor=anchor, fill=fill, expand=expand)

        links_options_pane = ttk.Panedwindow(mainwindow, orient="horizontal")
        links_options_notebook = ttk.Notebook(links_options_pane)
        links_options_notebook.configure(height=190,width=200)
        links_frame = ttk.Frame(links_options_notebook)
        links_frame.configure(width=400)
        create_spacer(links_frame, height=20, width=200, side="top")

        links_label = ttk.Label(links_frame)
        links_label.configure(
            font="TkCaptionFont",
            justify="right",
            text='Links File:')
        links_label.pack(anchor="w", padx=18, side="top")
        links_container = ttk.Frame(links_frame)
        links_container.configure(height=100,width=200)

        # Links File
        self.links_entry = ttk.Entry(links_container)
        self.links_entry.pack(anchor="w", expand=True, fill="x", padx=0, pady=10, side="left")
        default_links_path = "/home/init/Music/Youtube/yt-dl-gui/test.txt"
        self.links_entry.insert(0, default_links_path)
        self.links_browse = ttk.Button(links_container, text='Browse', command=self.browse_file)  # Changed command to self.browse_file
        self.links_browse.pack(anchor="e", expand=False, ipadx=20, padx=15, side="right")
        links_container.pack(anchor="w", fill="x", padx=15, side="top")
        cookies_label = ttk.Label(links_frame)
        cookies_label.configure(font="TkCaptionFont", text='Cookies File:')
        cookies_label.pack(anchor="w", ipady=5, padx=18, side="top")
        cookies_container = ttk.Frame(links_frame)
        cookies_container.configure(height=200,width=200)

        # Cookies Input
        self.cookies_entry = ttk.Entry(cookies_container)
        self.cookies_entry.pack(
            anchor="w",
            expand=True,
            fill="x",
            padx=0,
            pady=10,
            side="left")
        default_cookies_path = "/home/init/Downloads/cookies.txt"
        self.cookies_entry.insert(0, default_cookies_path)
        self.cookies_browse = ttk.Button(cookies_container)
        self.cookies_browse.configure(text='Browse', command=self.browse_cookies_file)
        self.cookies_browse.pack(anchor="e", expand=False, ipadx=20, padx=15, side="right")
        cookies_container.pack(anchor="w", fill="both", padx=15, side="top")
        links_frame.pack(anchor="w", side="left")
        links_options_notebook.add(links_frame, text='Links')
        paths_frame = ttk.Frame(links_options_notebook)
        # Output Directory
        output_dir_container = ttk.Frame(paths_frame)
        output_dir_container.configure(width=200)
        create_spacer(output_dir_container)
        output_dir_label = ttk.Label(output_dir_container)
        output_dir_label.configure(
            font="TkCaptionFont",
            justify="right",
            text='Output Directory:')
        output_dir_label.pack(anchor="w", expand=False, fill="x", side="top")
        create_spacer(links_frame, height=20, width=200, side="top")

        self.output_dir_entry = ttk.Entry(output_dir_container)
        self.output_dir_entry.pack(
            anchor="w",
            expand=True,
            fill="x",
            padx=0,
            pady=10,
            side="left")
        self.output_dir_browse = ttk.Button(output_dir_container)
        self.output_dir_browse.configure(text='Browse', command=self.browse_output_path)
        self.output_dir_browse.pack(anchor="e", expand=False, ipadx=20, padx=15, side="right")

        output_dir_container.pack(anchor="w", expand=True, fill="x", padx=15, side="left")
        paths_frame.pack(anchor="n", side="top")

        links_options_notebook.add(paths_frame, text='Paths')
        links_options_notebook.pack(anchor="w", fill="x", side="left")
        links_options_pane.add(links_options_notebook)
        links_options_pane.pack(
            expand=False,
            fill="both",
            ipadx=10,
            ipady=10,
            padx=15,
            pady=10,
            side="top")

        all_options_pane = ttk.Panedwindow(mainwindow, orient="horizontal")
        all_options_notebook = ttk.Notebook(all_options_pane)
        all_options_notebook.configure(height=170, width=200)

        frame38 = ttk.Frame(all_options_notebook)
        frame38.configure(borderwidth=1, height=100, width=400)

        frame41 = ttk.Frame(frame38)
        frame41.configure(height=20, width=200)
        frame41.pack(anchor="w", fill="both", padx=15, side="top")

        label10 = ttk.Label(frame38)
        label10.configure(font="TkCaptionFont",justify="right",text='Custom Options:')
        label10.pack(anchor="nw", padx=18, side="top")

        frame42 = ttk.Frame(frame38)
        frame42.configure(height=110)

        # Quality Check
        checkbutton1 = ttk.Checkbutton(frame42, style="Switch.TCheckbutton")
        checkbutton1.configure(state="normal", text='Best Quality', variable=self.quality_var)
        checkbutton1.pack(anchor="w", side="top")

        # Output Check
        checkbutton2 = ttk.Checkbutton(frame42, style="Switch.TCheckbutton")
        checkbutton2.configure(text='Format Output', variable=self.output_format_var)
        checkbutton2.pack(anchor="w", side="top")

        # Embed Metadata
        checkbutton3 = ttk.Checkbutton(frame42, style="Switch.TCheckbutton")
        checkbutton3.configure(text='Embed Metadata', variable=self.meta_data_var)
        checkbutton3.pack(anchor="w", side="top")

        frame42.pack(anchor="nw", padx=18, pady=15, side="left")

        frame51 = ttk.Frame(frame38)
        frame51.configure(width=200)
        frame51.pack(anchor="w", fill="both", padx=15, side="top")

        frame38.pack(anchor="w", side="left")

        all_options_notebook.add(frame38, text='Options')
        frame43 = ttk.Frame(all_options_notebook)

        frame44 = ttk.Frame(frame43)
        frame44.configure(borderwidth=2, width=200)
        frame45 = ttk.Frame(frame44)
        frame45.configure(width=200)
        frame45.pack(anchor="w", expand=True, fill="x", side="top")
        label12 = ttk.Label(frame44)
        label12.configure(
            font="TkCaptionFont",
            justify="right",
            text='Arguments:')
        label12.pack(anchor="w", expand=False, fill="x", side="top")

        # Custom Args
        self.entry14 = ttk.Entry(frame44)
        self.entry14.pack(
            anchor="w",
            expand=True,
            fill="x",
            padx=0,
            pady=10,
            side="left")
        frame44.pack(anchor="w", expand=True, fill="x", padx=15, side="left")
        frame43.pack(anchor="n", side="top")
        all_options_notebook.add(frame43, text='Custom Args')
        frame46 = ttk.Frame(all_options_notebook)
        frame46.configure(borderwidth=1, width=400)
        frame53 = ttk.Frame(frame46)
        frame53.configure(height=20, width=200)
        frame53.pack(anchor="w", fill="both", padx=15, side="top")
        frame48 = ttk.Frame(frame46)
        frame48.configure(width=200)


        self.entry17 = ttk.Entry(frame48, textvariable=self.resolution)
        self.entry17.configure(justify="right", width=10)
        self.entry17.pack(expand=True, fill="x", padx=15, side="right")

        # Sacad Check
        checkbutton4 = ttk.Checkbutton(frame48, style="Switch.TCheckbutton")
        checkbutton4.configure(
            takefocus=False,
            text='Update Covers with Sacad using resolution:', variable=self.sacad_var)
        checkbutton4.pack(anchor="w", side="top")
        frame48.pack(anchor="w", padx=18, side="top")
        frame50 = ttk.Frame(frame46)
        frame50.configure(width=200)
        frame56 = ttk.Frame(frame50)
        frame56.configure(height=110)

        # Album Art Check
        checkbutton5 = ttk.Checkbutton(frame56, style="Switch.TCheckbutton")
        checkbutton5.configure(text='Embed Album Art', variable=self.album_art_var)
        checkbutton5.pack(anchor="w", expand=True, fill="x", side="top")

        # Strip Unwanted ID3 Tags
        checkbutton6 = ttk.Checkbutton(frame56, style="Switch.TCheckbutton")
        checkbutton6.configure(text='Clean ID3 Tags', variable=self.strip_id3_var)
        checkbutton6.pack(anchor="w", expand=False, side="top")

        # Artist > AlbumArtist
        checkbutton7 = ttk.Checkbutton(frame56, style="Switch.TCheckbutton")
        checkbutton7.configure(text='Artist > AlbumArtist', variable=self.append_to_albumartist_var)
        checkbutton7.pack(anchor="w", expand=True, fill="x", side="top")
        frame56.pack(anchor="n", padx=18, pady=10, side="left")
        frame50.pack(anchor="w", expand=True, fill="x", side="top")
        frame46.pack(anchor="w", side="left")

        all_options_notebook.add(frame46, text='Post Processing')
        all_options_notebook.pack(anchor="w", fill="x", side="left")
        all_options_pane.add(all_options_notebook)
        all_options_pane.pack(
            anchor="center",
            expand=False,
            fill="both",
            ipadx=10,
            ipady=10,
            padx=15,
            pady=10,
            side="top")
        button15 = ttk.Button(mainwindow)

        # Download Button

        button15.configure(
            text='Download Playlist',
            style='Accent.TButton',
            command=self.validate_and_start_download  # Adjusted to the new intermediary method
        )

        button15.pack(anchor="w", expand=True, fill="x", padx=15, side="top")

        # Configuration for the log display font
        mainwindow.tk.call("font", "create", "SunValleyLogFont", "-family", "Segoe UI Variable Small", "-size", -13)

        frame27 = ttk.Frame(mainwindow)
        frame27.configure(height=20, width=200)

        label4 = ttk.Label(frame27)
        label4.configure(font="TkCaptionFont", text='Output Log:')
        label4.pack(anchor="w", expand=True, fill="x", pady=15, side="top")

        frame2 = ttk.Frame(frame27)
        frame2.configure(height=10, width=200)
        frame2.pack(anchor="w", expand=True, fill="x", side="left")

        frame27.pack(anchor="n", expand=True, fill="x", padx=15, side="left")

        # Create a Text widget for the log display
        self.log_widget = Text(frame2, wrap="none", relief="ridge", font="SunValleyLogFont", padx=10, pady=15)
        self.log_widget.pack(side="left", fill="both", expand=True)

        # Create a Scrollbar and attach it to the Text widget
        self.scrollbar = ttk.Scrollbar(frame2, orient="vertical", command=self.log_widget.yview)
        self.log_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        mainwindow.pack(expand=True, fill="both", pady=20, side="top")
        mainwindow.pack_propagate(False)

        # Main widget
        self.mainwindow = mainwindow

    def validate_output_dir(self):
        output_dir = self.output_dir_entry.get().strip()
        if not output_dir:
            def show_custom_error(message):
                dialog = tk.Toplevel()
                dialog.title("Error")
                tk.Label(dialog, text=message, font='SunValleyLogFont 12').pack(padx=20, pady=20)
                tk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 20))
                dialog.transient(root)  # Set to be on top of the main window
                dialog.grab_set()  # Modal focus
                root.wait_window(dialog)  # Wait for the dialog to be closed

            # Usage
            show_custom_error("Please set an output directory from the Paths tab.")
            return False
        return True

    def validate_and_start_download(self):
        if not self.validate_output_dir():
            return  # Exit if validation fails

        # Start the download process in a new thread if validation succeeds
        Thread(
            target=self.start_download, args=(self.links_entry.get(), self.get_options(), self.log_widget), daemon=True).start()

    def start_download(self, file_path, options, log_widget):
        with open(file_path, 'r') as file:
            urls = file.readlines()
        output_path = options['output_path'].rstrip('/') + '/' if options['output_path'] else ""
        download_processes = []  # List to track download subprocesses

        for url in urls:
            url = url.strip()
            if url:
                command = 'yt-dlp --progress --newline'
                if options['best_quality']:
                    command += ' -x'
                cookies_path = options['cookies']
                if cookies_path:
                    command += f' --cookies {shlex.quote(cookies_path)}'
                command += f' -o "{output_path}%(playlist_title)s/%(playlist_autonumber)02d. %(title)s.%(ext)s"'
                if options['meta_data']:
                    command += ' --add-metadata --embed-metadata --extract-audio --embed-thumbnail'
                    command += ' --parse-metadata "playlist_index:%(track_number)s"'
                if options['album_art']:
                    command += ' --ppa "ThumbnailsConvertor+FFmpeg_o:-c:v mjpeg -vf crop=\\\'if(gt(ih,iw),iw,ih):if(gt(iw,ih),ih,iw)\\\'"'
                if options['custom_args']:
                    command += f' {options["custom_args"]}'
                command += f' {shlex.quote(url)}'

                self.update_log("Executing command: " + command + "\n")

                process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)

                for line in process.stdout:
                    if '[download]' in line or 'WARNING:' in line or 'ERROR:' in line:
                        self.update_log(line)
                process.wait()

                random_sleep_time = random.uniform(0.2, 2)
                time.sleep(random_sleep_time)


        # Wait for all downloads to complete
        for process in download_processes:
            process.wait()

        if options['strip_id3'] or options['append_to_albumartist']:
            self.update_log(f"Output path is set to: {output_path}")
            self.process_directory(output_path, log_widget)
        if options['sacad']:
            self.update_log(f"Running sacad_r with cover resolution {self.resolution.get()}")
            default_file_name = "folder.jpg"  # Assuming this is your default file name
            self.run_sacad(output_path, default_file_name)

    def toggle_theme(self):
        current_theme = svc_ttk.get_theme()
        if current_theme == "dark":
            svc_ttk.set_theme("light")
            # Update label images for light theme
            self.logo_label.configure(image=self.img_logo_light)
            self.blurb_label.configure(image=self.img_blurb_light)
        else:
            svc_ttk.set_theme("dark")
            # Update label images for dark theme
            self.logo_label.configure(image=self.img_logo_dark)
            self.blurb_label.configure(image=self.img_blurb_dark)

    def process_directory(self, directory_path, log_widget):
        self.update_log(f"Starting to process directory: {directory_path}")
        found_files = False
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                found_files = True
                self.update_log(f"Found file: {file}")
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                if ext.lower() in ['.m4a', '.mp4', '.opus']:
                    self.update_and_clean_tags(file_path, tags_to_remove)
        if not found_files:
            self.update_log("No files found in directory.")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            self.links_entry.delete(0, tk.END)  # Use self.links_entry
            self.links_entry.insert(0, filename)  # Use self.links_entry

    def browse_cookies_file(self):
        cookies_filename = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if cookies_filename:
            self.cookies_entry.delete(0, tk.END)
            self.cookies_entry.insert(0, cookies_filename)

    def browse_output_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)


    def update_and_clean_tags(self, input_file, tags_to_remove):
        _, ext = os.path.splitext(input_file)
        ext = ext.lower()
        #print(f"Processing file: {input_file}")  # Debugging
        album_artist_field = 'album_artist' if ext in ['.m4a', '.mp4'] else 'ALBUMARTIST' if ext == '.opus' else None

        if not album_artist_field:
            print(f"Unsupported file extension for file: {input_file}")  # Provide more context in the print statement
            return

        cmd = ['ffprobe', '-loglevel', 'error', '-show_entries', 'format_tags=artist', '-of',
               'default=noprint_wrappers=1:nokey=1', input_file]
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        original_artist_name = process.stdout.strip()

        modified_artist_name = re.sub(r'^([^,]+),.*$', r'\1', original_artist_name)
        if not original_artist_name:
            modified_artist_name = ""

        base_name = os.path.splitext(input_file)[0]
        temp_file = f"{base_name}.tmp{ext}"

        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-metadata', f'{album_artist_field}={modified_artist_name}',
            '-codec', 'copy'
        ]

        for tag in tags_to_remove:
            cmd += ['-metadata', f"{tag}="]

        cmd.append(temp_file)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            os.remove(input_file)
            os.rename(temp_file, input_file)
            self.update_log(f"Updated and cleaned {input_file}")
        else:
            os.remove(temp_file)
            self.update_log(f"Error processing {input_file}: {result.stderr}")

    def run_sacad(self, input_folder, name):
        resolution = self.resolution.get()  # Using the resolution from the class directly
        command = ['sacad_r', '-i', input_folder, resolution, name]
        command_str = " ".join(shlex.quote(arg) for arg in command)
        self.update_log(f"Executing sacad command: {command_str}")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)

            output, errors = process.communicate()  # This waits for the process to finish and captures output
            for line in output.splitlines():
                self.update_log(line)
            if errors:
                self.update_log(errors)

        except FileNotFoundError:
            self.update_log("Sacad not found. Please install via 'pip install sacad'")

    def get_options(self):
        return {
            'best_quality': self.quality_var.get(),
            'cookies': self.cookies_entry.get(),
            'output_format': self.output_format_var.get(),
            'meta_data': self.meta_data_var.get(),
            'album_art': self.album_art_var.get(),
            'custom_args': self.entry14.get(),
            'output_path': self.output_dir_entry.get(),
            'strip_id3': self.strip_id3_var.get(),
            'append_to_albumartist': self.append_to_albumartist_var.get(),
            'sacad': self.sacad_var.get(),
            'resolution': self.resolution.get()
        }
    def update_log(self, message):
        cleaned_message = message.rstrip('\n').rstrip('\r') + "\n"
        # Using lambda to ensure thread-safe updates to the Tkinter widget
        self.master.after(0, lambda: self.log_widget.insert(tk.END, cleaned_message))
        self.master.after(0, lambda: self.log_widget.see(tk.END))
    def run(self):
        self.mainwindow.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("DL-YTP  (Youtube Music Helper)")
    app = MainApp(root)
    app.run()
