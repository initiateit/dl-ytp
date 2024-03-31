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

list_tags_to_remove = ['comment', 'description', 'synopsis', 'Long Description']


class MainApp:

    def __init__(self, master=None):

        self.master = master

        # Options
        self.no_transcode_var = tk.BooleanVar(value=True)
        self.output_format_var = tk.BooleanVar(value=True)
        self.random_sleep_var = tk.BooleanVar(value=True)

        self.restrict_filename_var = tk.BooleanVar(value=True)
        self.no_mtime_var = tk.BooleanVar(value=True)

        self.strip_id3_var = tk.BooleanVar(value=False)
        self.append_to_albumartist_var = tk.BooleanVar(value=False)
        self.meta_data_var = tk.BooleanVar(value=True)
        # Post Processing
        self.use_youtube_var = tk.BooleanVar(value=False)
        self.yt_embed_albumart_var = tk.BooleanVar(value=False)
        self.yt_extract_albumart_var = tk.BooleanVar(value=False)

        self.use_sacad_var = tk.BooleanVar(value=False)
        self.sacad_dl_albumart = tk.BooleanVar(value=False)
        self.sacad_embed_albumart = tk.BooleanVar(value=False)

        self.album_art_var = tk.BooleanVar(value=False)
        self.resolution = tk.StringVar(value="1000")

        self.num_threads_var = tk.StringVar(value="1")
        self.max_rate_var = tk.StringVar(value="1250000")

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
        links_options_notebook.configure(height=190, width=200)

        links_frame = ttk.Frame(links_options_notebook)
        links_frame.configure(width=400)

        create_spacer(links_frame, height=20, width=200, side="top")

        links_label = ttk.Label(links_frame)
        links_label.configure(font="TkCaptionFont", justify="right", text='Links File:')
        links_label.pack(anchor="w", padx=18, side="top")
        links_container = ttk.Frame(links_frame)
        links_container.configure(height=100, width=200)

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
        cookies_container.configure(height=200, width=200)

        # Cookies Input
        self.cookies_entry = ttk.Entry(cookies_container)
        self.cookies_entry.pack(anchor="w", expand=True, fill="x", padx=0, pady=10, side="left")
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
        output_dir_label.configure(font="TkCaptionFont", justify="right", text='Output Directory:')
        output_dir_label.pack(anchor="w", expand=False, fill="x", side="top")
        create_spacer(links_frame, height=20, width=200, side="top")

        self.output_dir_entry = ttk.Entry(output_dir_container)
        self.output_dir_entry.pack(anchor="w", expand=True, fill="x", padx=0, pady=10, side="left")
        self.output_dir_browse = ttk.Button(output_dir_container)
        self.output_dir_browse.configure(text='Browse', command=self.browse_output_path)
        self.output_dir_browse.pack(anchor="e", expand=False, ipadx=20, padx=15, side="right")

        output_dir_container.pack(anchor="w", expand=True, fill="x", padx=15, side="left")
        paths_frame.pack(anchor="n", side="top")

        links_options_notebook.add(paths_frame, text='Paths')
        links_options_notebook.pack(anchor="w", fill="x", side="left")
        links_options_pane.add(links_options_notebook)
        links_options_pane.pack(expand=False, fill="both", ipadx=10, ipady=10, padx=15, pady=10, side="top")

        settings_pane = ttk.Panedwindow(mainwindow, orient="horizontal")
        settings_notebook = ttk.Notebook(settings_pane)
        settings_notebook.configure(height=190, width=200)
        options_container = ttk.Frame(settings_notebook)
        options_container.configure(borderwidth=1, height=110, width=400)

        simple_frame = ttk.Frame(options_container)
        simple_frame.configure(height=110)

        simple_label = ttk.Label(simple_frame)
        simple_label.configure(font="TkCaptionFont", text='Simple')
        simple_label.pack(anchor="n", fill="x", side="top")

        simple_separator = ttk.Separator(simple_frame)
        simple_separator.configure(orient="horizontal")
        simple_separator.pack(anchor="n", expand=False, fill="x", pady=10, side="top")

        simple_checkbox_container = ttk.Frame(simple_frame)
        simple_checkbox_container.configure(height=200, width=200)

        no_transcode_checkbox = ttk.Checkbutton(simple_checkbox_container)
        no_transcode_checkbox.configure(text='No Audio transcode', variable=self.no_transcode_var)
        no_transcode_checkbox.pack(anchor="n", fill="x", side="top")

        format_output_checkbox = ttk.Checkbutton(simple_checkbox_container)
        format_output_checkbox.configure(compound="left", text='Format Output')
        format_output_checkbox.pack(anchor="n", fill="x", side="top")
        randon_sleep_checkbox = ttk.Checkbutton(simple_checkbox_container)
        randon_sleep_checkbox.configure(compound="right", text='Random Sleep Delay')
        randon_sleep_checkbox.pack(anchor="n", pady=5, side="top")

        simple_checkbox_container.pack(anchor="n", side="top")
        simple_frame.pack(anchor="nw", fill="x", padx=18, pady=10, side="left")

        advanced_options_frame = ttk.Frame(options_container)
        advanced_options_frame.configure(height=200)

        advanced_label = ttk.Label(advanced_options_frame)
        advanced_label.configure(font="TkCaptionFont", text='Advanced')
        advanced_label.pack(anchor="n", fill="x", side="top")

        advanced_label = ttk.Separator(advanced_options_frame)
        advanced_label.configure(orient="horizontal")
        advanced_label.pack(anchor="n", expand=False, fill="x", pady=10, side="top")

        advanced_frame1 = ttk.Frame(advanced_options_frame)
        advanced_frame1.configure(height=100)

        restrict_filenames_checkbox = ttk.Checkbutton(advanced_frame1)
        restrict_filenames_checkbox.configure(text='Restrict Filenames', variable=self.restrict_filename_var)
        restrict_filenames_checkbox.pack(anchor="w", expand=False, fill="both", side="top")

        no_mtime_checkbox = ttk.Checkbutton(advanced_frame1)
        no_mtime_checkbox.configure(text='Dont set mtime', variable=self.no_mtime_var)
        no_mtime_checkbox.pack(anchor="w", expand=False, fill="both", side="top")

        num_threads_label = ttk.Label(advanced_frame1)
        num_threads_label.configure(takefocus=True, text='Num Threads: ')
        num_threads_label.pack(anchor="w", fill="x", ipady=4, padx=5, side="left")

        num_threads_entry = ttk.Entry(advanced_frame1, textvariable=self.num_threads_var)
        num_threads_entry.configure(validate="key", width=5)
        num_threads_entry.pack(anchor="e", side="right")

        advanced_frame1.pack(anchor="n", fill="x", side="top")

        advanced_frame2 = ttk.Frame(advanced_options_frame)
        advanced_frame2.configure(height=200, width=200)

        max_rate_label = ttk.Label(advanced_frame2)
        max_rate_label.configure(justify="right", text='Max Rate: ')
        max_rate_label.pack(anchor="w", fill="x", ipady=4, padx=5, pady=5, side="left")

        max_rate_entry = ttk.Entry(advanced_frame2)
        max_rate_entry.configure(width=5, textvariable=self.max_rate_var)
        max_rate_entry.pack(anchor="e", pady=5, side="right")

        advanced_frame2.pack(anchor="w", fill="x", side="top")
        advanced_options_frame.pack(anchor="n", fill="both", padx=10, pady=10, side="left")

        tag_options_frame = ttk.Frame(options_container)
        tag_options_frame.configure(height=100)

        tag_options_label = ttk.Label(tag_options_frame)
        tag_options_label.configure(font="TkCaptionFont", text='Tag Options')
        tag_options_label.pack(anchor="n", fill="x", side="top")

        tag_options_separator = ttk.Separator(tag_options_frame)
        tag_options_separator.configure(orient="horizontal")
        tag_options_separator.pack(anchor="n", expand=False, fill="x", pady=10, side="top")

        tag_options_container = ttk.Frame(tag_options_frame)
        tag_options_container.configure(height=110)

        clean_id3_checkbox = ttk.Checkbutton(tag_options_container)
        clean_id3_checkbox.configure(text='Clean ID3 Tags')
        clean_id3_checkbox.pack(anchor="w", expand=False, fill="both", side="top")

        artist_albumartist_checkbox = ttk.Checkbutton(tag_options_container)
        artist_albumartist_checkbox.configure(text='Artist > AlbumArtist')
        artist_albumartist_checkbox.pack(anchor="n", fill="x", side="top")

        embed_metadata_checkbox = ttk.Checkbutton(tag_options_container)
        embed_metadata_checkbox.configure(text='Embed Metadata')
        embed_metadata_checkbox.pack(anchor="w", side="top")

        tag_options_container.pack(anchor="n", expand=True, fill="both", side="left")
        tag_options_frame.pack(anchor="e", expand=True, fill="both", padx=10, pady=10, side="left")

        options_container.pack(anchor="w", side="left")
        settings_notebook.add(options_container, text='Options')

        post_processing_container = ttk.Frame(settings_notebook)
        post_processing_container.configure(borderwidth=1, width=600)

        use_youtube_container = ttk.Frame(post_processing_container)
        use_youtube_container.configure(height=100, width=300)

        use_youtube_checkbox = ttk.Checkbutton(use_youtube_container)
        use_youtube_checkbox.configure(text='Use Youtube For Covers')
        use_youtube_checkbox.pack(anchor="w", side="top")

        use_youtube_separator = ttk.Separator(use_youtube_container)
        use_youtube_separator.configure(orient="horizontal")
        use_youtube_separator.pack(anchor="n", fill="x", padx=10, pady=10, side="top")

        use_youtube_frame = ttk.Frame(use_youtube_container)
        use_youtube_frame.configure(height=200)

        yt_embed_albumart_checkbox = ttk.Checkbutton(use_youtube_frame)
        yt_embed_albumart_checkbox.configure(takefocus=False, text='Embed AlbumArt')
        yt_embed_albumart_checkbox.pack(anchor="w", fill="x", side="top")

        yt_extract_albumart_checkbox = ttk.Checkbutton(use_youtube_frame)
        yt_extract_albumart_checkbox.configure(text='Extract AlbumArt')
        yt_extract_albumart_checkbox.pack(anchor="w", fill="x", side="top")

        yt_albumart_name_label = ttk.Label(use_youtube_frame)
        yt_albumart_name_label.configure(text='Name:')
        yt_albumart_name_label.pack(anchor="n", ipady=4, pady=5, side="left")

        yt_albumart_name_entry = ttk.Entry(use_youtube_frame)
        yt_albumart_name_entry.configure(justify="right", width=10)
        yt_albumart_name_entry.pack(anchor="n", padx=5, pady=5, side="left")

        use_youtube_frame.pack(anchor="w", fill="both", side="top")
        use_youtube_container.pack(anchor="n", expand=False, fill="both", padx=10, pady=10, side="left")

        use_sacad_container = ttk.Frame(post_processing_container)
        use_sacad_container.configure(height=200, width=300)

        use_sacad_checkbox = ttk.Checkbutton(use_sacad_container)
        use_sacad_checkbox.configure(text='Use Sacad For Covers')
        use_sacad_checkbox.pack(anchor="w", side="top")

        use_sacad_separator = ttk.Separator(use_sacad_container)
        use_sacad_separator.configure(orient="horizontal")

        use_sacad_separator.pack(anchor="n", expand=False, fill="x", padx=10, pady=10, side="top")

        use_sacad_frame = ttk.Frame(use_sacad_container)
        use_sacad_frame.configure(height=100)

        sacad_frame_1 = ttk.Frame(use_sacad_frame)
        sacad_frame_1.configure(height=200, width=200)

        sacad_download_cover_checkbox = ttk.Checkbutton(sacad_frame_1)
        sacad_download_cover_checkbox.configure(takefocus=False, text='Download Cover')
        sacad_download_cover_checkbox.pack(anchor="n", expand=False, fill="x", side="top")

        sacad_embed_cover_checkbox = ttk.Checkbutton(sacad_frame_1)
        sacad_embed_cover_checkbox.configure(text='Embed Cover')
        sacad_embed_cover_checkbox.pack(anchor="n", fill="x", side="top")

        sacad_resolution_label = ttk.Label(sacad_frame_1)
        sacad_resolution_label.configure(text='Resolution: ', width=10)
        sacad_resolution_label.pack(anchor="nw", ipady=4, pady=5, side="left")
        sacad_resolution_entry = ttk.Entry(sacad_frame_1)
        sacad_resolution_entry.configure(justify="right", width=10)
        sacad_resolution_entry.pack(anchor="nw", fill="x", padx=5, pady=5, side="left")

        sacad_frame_1.pack(anchor="n", fill="x", side="left")

        use_sacad_frame.pack(anchor="n", fill="x", side="top")
        use_sacad_frame_2 = ttk.Frame(use_sacad_container)
        use_sacad_frame_2.configure(height=200, width=200)

        sacad_cover_name_label = ttk.Label(use_sacad_frame_2)
        sacad_cover_name_label.configure(text='Name: ', width=10)
        sacad_cover_name_label.pack(anchor="n", fill="x", ipady=4, side="left")

        sacad_cover_name_entry = ttk.Entry(use_sacad_frame_2)
        sacad_cover_name_entry.configure(justify="right", width=10)
        sacad_cover_name_entry.pack(anchor="nw", expand=False, fill="x", padx=5, side="left")

        use_sacad_frame_2.pack(anchor="s", fill="x", side="bottom")
        use_sacad_frame_2.pack_propagate(False)
        use_sacad_container.pack(anchor="n", expand=False, fill="both", padx=20, pady=10, side="left")

        post_processing_container.pack(anchor="n", expand=True, fill="both", side="left")
        settings_notebook.add(post_processing_container, text='Post Processing')

        custom_args_container = ttk.Frame(settings_notebook)

        custom_args_frame = ttk.Frame(custom_args_container)
        custom_args_frame.configure(borderwidth=2, width=200)

        custom_args_spacer = ttk.Frame(custom_args_frame)
        custom_args_spacer.configure(width=200)
        custom_args_spacer.pack(anchor="w", expand=True, fill="x", side="top")

        custom_args_label = ttk.Label(custom_args_frame)
        custom_args_label.configure(font="TkDefaultFont", justify="right", text='Enter custom command line arguments:')
        custom_args_label.pack(anchor="w", expand=False, fill="x", padx=5, pady=20, side="top")

        self.custom_args_entry = ttk.Entry(custom_args_frame)
        self.custom_args_entry.pack(anchor="w", fill="both", padx=0, pady=10, side="top")

        custom_args_frame.pack(anchor="w", expand=False, fill="x", padx=15, pady=18, side="top")
        custom_args_container.pack(anchor="w", fill="both", side="top")

        settings_notebook.add(custom_args_container, text='Custom Args')
        settings_notebook.pack(anchor="w", fill="x", side="left")
        settings_pane.add(settings_notebook)
        settings_pane.pack(anchor="center", expand=False, fill="both", ipadx=10, ipady=10, padx=10, pady=10, side="top")

        download_button = ttk.Button(mainwindow)

        # Download Button

        download_button.configure(
            text='Download Playlist',
            style='Accent.TButton',
            command=self.validate_and_start_download  # Adjusted to the new intermediary method
        )

        download_button.pack(anchor="w", expand=True, fill="x", padx=15, side="top")

        # Configuration for the log display font
        mainwindow.tk.call("font", "create", "SunValleyLogFont", "-family", "Segoe UI Variable Small", "-size", -13)

        output_log_container = ttk.Frame(mainwindow)
        output_log_container.configure(height=20, width=200)

        output_log_label = ttk.Label(output_log_container)
        output_log_label.configure(font="TkCaptionFont", text='Output Log:')
        output_log_label.pack(anchor="w", expand=True, fill="x", pady=15, side="top")

        output_log_frame = ttk.Frame(output_log_container)
        output_log_frame.configure(height=10, width=200)
        output_log_frame.pack(anchor="w", expand=True, fill="x", side="left")

        output_log_container.pack(anchor="n", expand=True, fill="x", padx=15, side="left")

        # Create a Text widget for the log display
        self.log_widget = Text(output_log_frame, wrap="none", relief="ridge", font="SunValleyLogFont", padx=10, pady=15)
        self.log_widget.pack(side="left", fill="both", expand=True)

        # Create a Scrollbar and attach it to the Text widget
        self.scrollbar = ttk.Scrollbar(output_log_frame, orient="vertical", command=self.log_widget.yview)
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

    def start_download(self, file_path, options):
        with open(file_path, 'r') as file:
            urls = file.readlines()
        output_path = options['output_path'].rstrip('/') + '/' if options['output_path'] else ""
        download_processes = []  # List to track download subprocesses

        for url in urls:
            url = url.strip()
            if url:
                command = 'yt-dlp --progress --newline'
                if options['no_transcode']:
                    command += ' -x'
                if options['output_format']:
                    command += f' -o "{output_path}%(playlist_title)s/%(playlist_autonumber)02d. %(title)s.%(ext)s"'
                if options['random_sleep']:
                    random_sleep_time = random.uniform(0.2, 2)
                    command += f' --sleep-interval {random_sleep_time}'
                if options['restrict_filenames']:
                    command += ' --restrict-filenames'
                if options['no_mtime']:
                    command += ' --no-mtime'
                if options['num_threads']:
                    command += f' -N {options["num_threads"]}'
                else:
                    command += f' -N 1'
                if options['max_rate']:
                    try:
                        return float(self.max_rate_var.get())
                    except ValueError:
                        return self.max_rate_var

                cookies_path = options['cookies']
                if cookies_path:
                    command += f' --cookies {shlex.quote(cookies_path)}'

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
            self.process_directory(output_path)
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

    def process_directory(self, directory_path):
        self.update_log(f"Starting to process directory: {directory_path}")
        found_files = False
        for current_dir, dirs, files in os.walk(directory_path):
            for file in files:
                found_files = True
                self.update_log(f"Found file: {file}")
                file_path = os.path.join(current_dir, file)
                _, ext = os.path.splitext(file_path)
                if ext.lower() in ['.m4a', '.mp4', '.opus']:
                    self.update_and_clean_tags(file_path, list_tags_to_remove)
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
        # print(f"Processing file: {input_file}")  # Debugging
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
            'cookies': self.cookies_entry.get(),
            'output_path': self.output_dir_entry.get(),

            'no_transcode': self.no_transcode_var.get(),
            'output_format': self.output_format_var.get(),
            'random_sleep': self.random_sleep_var.get(),

            'restrict_filenames': self.restrict_filename_var.get(),
            'no_mtime': self.no_mtime_var.get(),
            'num_threads': self.num_threads_var.get(),
            'max_rate': self.max_rate_var.get(),

            'strip_id3': self.strip_id3_var.get(),
            'append_to_albumartist': self.append_to_albumartist_var.get(),
            'meta_data': self.meta_data_var.get(),
            'use_youtube': self.use_youtube_var.get(),
            'use_yt_albumart': self.album_art_var.get(),
            # 'yt_albumart_name':

            'use_sacad': self.use_sacad_var.get(),
            'use_sacad_albumart': self.sacad_dl_albumart.get(),
            'resolution': self.resolution.get(),

            'custom_args': self.custom_args_entry.get()

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
