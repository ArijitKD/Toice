# -*- coding: utf8 -*-

# Background image by rawpixel.com on Freepik
# Link: https://www.freepik.com/free-vector/dark-gradient-background-with-copy-space_14731307.htm

# Gear icon on Settings button by rawpixel.com on Freepik
# Link: https://www.freepik.com/free-vector/illustration-cogwheel_2609999.htm

# Play button image from: https://www.pngwing.com/en/free-png-zazqa

# Pause button image from: https://www.pngwing.com/en/free-png-zqngb

# Stop button image from: https://www.pngwing.com/en/free-png-ajmth

# Speaker (loud) image from: https://commons.wikimedia.org/wiki/File:Speaker_Icon.svg

# Speaker (muted) image from: https://commons.wikimedia.org/wiki/File:Mute_Icon.svg

# Loop button image from: https://www.pngwing.com/en/free-png-amytq

# Save button from: https://www.pngegg.com/en/png-zelil

# About icon from: https://www.pngegg.com/en/png-oayss

# Font used: Noto Sans


import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mbox
from tkinter.scrolledtext import ScrolledText

import customtkinter as ctk
from pygame import mixer
from PIL import Image, ImageTk
import pydub

import os
from shutil import copy
from subprocess import Popen, PIPE
import time
from platform import system

from settingsmenu import ToiceSettingsMenu
import ttshandler as ttsh

APPNAME = "Toice"

DIRS_IN_USERDIR = {
        "IMAGE": "images/",
        "CACHE": "cache/"
        }

DEFAULT_UI_LANG = \
'''
LanguageName = English (US)
TextboxPlaceholderLabel = Enter your text here...

WaveformLabelNormal = Click the Play button to generate Text to Speech
WaveformLabelGenerating = Generating Text to Speech audio...
WaveformLabelPlaying = Playing Now
WaveformLabelPaused = Speech Paused
WaveformLabelStopped = Speech Stopped
WaveformLabelNoTextAlert = Type some text to get audio feedback
WaveformLabelTTSNotGeneratedAlert = Nothing to Save<BREAK>No speech has been generated yet
WaveformLabelNoConnectionAlert = You are offline<BREAK>To use GTTS, you must be online
WaveformLabelUnknownErrorAlert = Oops! Something bad happened :(

SettingsMenuTitle = Preferences
SaveDialogTitle = Save Speech Audio
AboutTitle = About Toice

UILanguageChangeAlert = You have changed the UI language of Toice. To apply this change, Toice needs to restart.<BREAK><BREAK>Do you want to restart now?

ChooseAPILabel = API to be used for Text to Speech

GeneralTabName = General
GTTSTabName = GTTS
Pyttsx3TabName = Pyttsx3

UILanguageLabel = UI Language

Pyttsx3SpeedLabel = Speech Rate (Words per minute)
Pyttsx3VolumeLabel = Speech Volume (Percentage)
Pyttsx3VoiceLabel = Voice to be used
Pyttsx3NoVoiceError = No voice packs installed
Pyttsx3VoiceinfoLabel = Gender supported by selected voice
Pyttsx3VoiceGenderMale = Male
Pyttsx3VoiceGenderFemale = Female
Pyttsx3VoiceGenderUnknown = Unknown

ButtonApply = Apply
ButtonCancel = Cancel
ButtonOK = OK
'''

ROOTDIR = os.path.dirname(__file__).replace("\\", "/")+"/"

if (ROOTDIR == '/'):
    ROOTDIR = ''

if (system() == "Windows"):
    USERDIR = os.environ["LOCALAPPDATA"]+"\\"+APPNAME+"\\".replace("\\", "/")
elif (system() == "Darwin"):
    USERDIR = os.path.expanduser("~/Library/%s/"%APPNAME)
else:
    USERDIR = os.path.expanduser("~/.%s/"%APPNAME.lower())

CONFIG_FILE = USERDIR+"config.cfg"

DEFAULT_CONFIG = \
f'''
WindowWidth = 1024
WindowHeight = 576
WindowX = 50
WindowY = 50
WindowMaximized = 0

TextboxFG = black
TextboxBG = white

LastSavedInDirectory = {os.path.expanduser('~')}

FontSize = 20

AudioVolume = 67
LoopAudio = 1

UILanguage = English (US)

Pyttsx3Speed = 150
Pyttsx3Volume = 67 
Pyttsx3VoiceID = 0

APIInUse = Pyttsx3
'''

SUCCESS = 0
FAILURE = 1


class Toice(tk.Tk):

    def __init__(self, logging=False):

        # Init super
        super().__init__()
        self.withdraw()

        self.icon = None
        try:
            self.icon = ImageTk.PhotoImage(Image.open(ROOTDIR+"assets/toice.png").resize((64, 64), Image.LANCZOS))
            self.wm_iconphoto(True, self.icon)
        except FileNotFoundError:
            self.log ("App icon not found!")

        # Init pygame mixer for audio playback
        mixer.init()

        # Keep track of whether the Noto Sans font is being installed
        self.installed_font = False

        # Font files
        self.font_file = os.path.join(ROOTDIR, "fonts/NotoSans-Regular.ttf")
        self.font_file_linux = os.path.expanduser("~/.local/share/fonts/NotoSans-Regular.ttf")
        self.font_file_macos = os.path.expanduser("~/Library/Fonts/NotoSans-Regular.ttf")

        # Noto Sans font will be loaded for Linux/MacOS systems
        font_load_status = self.load_notosans_font()

        # Default values
        self.logging = logging
        self.log_count = 1
        self.orig_image = None
        self.bg_image = None
        self.tkbg_image = None
        self.accent_color = "#25003e" #'#060e32'
        self.dominant_color_rgb = (6, 14 ,50)
        self.antiaccent_color = self.get_complementory(self.dominant_color_rgb)
        self.defcon = self.get_default()
        self.defuilang = self.get_default(datatype="uilang")
        self.config = {}
        self.uilang = {}

        self.ttspath = ""
        self.text = ""
        self.paused = False
        self.settings_changed = False
        self.error_occured = False
        self.audio_length = 0

        self.configure(background=self.accent_color)

        # Default widget values
        '[TEXTBOX]'
        self.textbox = None

        '[TOOL FRAME]'
        self.tool_frame = None

        '[WAVEFORM]'
        self.waveform_frame = None

        '[SEEKER]'
        self.seeker_frame = None

        '[GENERATE BUTTON]'
        self.generatebtn_frame = None

        '[CONTROL PANEL]'
        self.control_frame = None

        # Set app attributes
        self.title(APPNAME)
        self.minsize(1024, 576)

        # Set exit protocol
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # Check available language packs and remove invalid ones
        self.supported_ui_langs = {}
        invalid_lang_files = []

        try:
            languages = os.listdir(ROOTDIR+"languages")
            if (len(languages) == 0):
                raise FileNotFoundError
            for lang in languages:
                abslangpath = ROOTDIR+"languages/"+lang
                with open(abslangpath, encoding='UTF-8') as langfile:
                    strings = langfile.readlines()
                    for i in range(len(strings)):
                        try:
                            if (strings[i].strip() == ''):
                                strings.pop(i)
                        except IndexError:
                            break
                    if (len(strings) == 0):
                        invalid_lang_files.append(abslangpath)
                    elif (not (strings[0].startswith("LanguageName") and strings[0].find("=") != -1)):
                        invalid_lang_files.append(abslangpath)
                    else:
                        line = strings[0]
                        langname = line[line.index('=')+1::].strip()
                        self.supported_ui_langs[langname] = abslangpath

        except FileNotFoundError:
            self.log ("Missing language packs! Will load default language pack for UI: %s"%self.defcon["UILanguage"])
            os.makedirs(ROOTDIR+"languages", exist_ok=True)
            with open(ROOTDIR+"languages/en-us.lang", 'w', encoding='UTF-8') as langfile:
                lines = DEFAULT_UI_LANG.split("\n")
                for line in lines:
                    if (line.find('=') != -1):
                        langfile.writelines([line+"\n"])
            self.supported_ui_langs[self.defcon["UILanguage"]] = ROOTDIR+"languages/en-us.lang"
        

        for langfile in invalid_lang_files:
            self.log ("Removing invalid language file: %s"%langfile)
            os.remove(langfile)

        # Load configuration settings
        self.load_settings()

        # Loop setting
        if (self.config["LoopAudio"] == "0"):
            self.loops = 0
        else:
            self.loops = -1

        # Theme
        ctk.set_appearance_mode('dark')

        # Load the language pack
        self.load_ui_lang(lang=self.config["UILanguage"], langfile=self.supported_ui_langs[self.config["UILanguage"]])
        if (self.defuilang.keys() == self.uilang.keys()):
            self.log ("Loaded language pack: %s"%(self.config["UILanguage"]))
        else:
            self.log ("Failed to load language pack %s from %s (Missing/Invalid keys detected)"%(self.config["UILanguage"], self.supported_ui_langs[self.config["UILanguage"]]), logtype="ERROR")
            self.log ("Falling back to default language pack: %s"%(self.defcon["UILanguage"]))
            self.uilang = self.defuilang
            self.config["UILanguage"] = self.defcon["UILanguage"]

        # Default values
        self.lastwinwidth = self.config["WindowWidth"]
        self.lastwinheight = self.config["WindowHeight"]

        # Set the UI font
        if (system() == "Windows"):
            self.log ("Detected Windows system, Segoe UI font will be used for UI")
            self.font = ("Segoe UI", int(self.config["FontSize"]))
        else:
            if (font_load_status == SUCCESS):
                self.log ("Detected Linux/MacOS system, Noto Sans font will be used for UI")
                self.font = ("Noto Sans Regular", int(self.config["FontSize"]))
            else:
                self.log (f"Detected unsupported system! {APPNAME} will close")
                mbox.showerror (f"Your system is currently unsupported. {APPNAME} will not run.")
                self.destroy()
                raise SystemExit(1)

        # Set maximization
        if (self.config["WindowMaximized"] == "1"):
            self.maximize(True)

        # Set the geometry
        if ((int(self.config["WindowX"]) < int(self.defcon["WindowX"])) or ((int(self.config["WindowWidth"])+int(self.config["WindowX"]))>self.winfo_screenwidth())):
            self.set_default("WindowX")
        if ((int(self.config["WindowY"]) < int(self.defcon["WindowY"])) or ((int(self.config["WindowHeight"])+int(self.config["WindowY"]))>self.winfo_screenheight())):
            self.set_default("WindowY")
        self.geometry("%sx%s+%s+%s"%(self.config["WindowWidth"], self.config["WindowHeight"], self.config["WindowX"], self.config["WindowY"]))

        # Setup canvas
        self.background = ctk.CTkCanvas(self, highlightthickness=0, bg=self.accent_color)
        self.background.pack(fill=tk.BOTH, expand=True)

        # Add the widgets
        self.add_widgets()


    def load_notosans_font(self):
        try:
            if (system() == 'Darwin'):
                if (not os.path.isfile(self.font_file_macos)):
                    copy(self.font_file, self.font_file_macos)
                    self.installed_font = True
            elif (system() == "Linux"):
                if (not os.path.isfile(self.font_file_linux)):
                    copy(self.font_file, self.font_file_linux)
                    Popen(["fc-cache", "-fv"], stdout=PIPE, stderr=PIPE, shell=False)
                    self.installed_font = True
            else:
                return FAILURE
            return SUCCESS
        except FileNotFoundError:
            return FAILURE


    def unload_notosans_font(self):
        if (self.installed_font):
            try:
                if (system() == 'Darwin'):
                    os.remove(self.font_file_macos)
                else:
                    os.remove(self.font_file_linux)
                    Popen(["fc-cache", "-fv"], stdout=PIPE, stderr=PIPE, shell=False)
            except FileNotFoundError:
                return FAILURE
        return SUCCESS


    def audio_playing(self):
        return (mixer.music.get_busy() or self.paused)


    def pause_unpause_audio(self):
        if (self.audio_playing()):
            if (not self.paused):
                mixer.music.pause()
                self.paused = True
                self.waveform_label.configure(text=self.uilang["WaveformLabelPaused"])
                self.playpausebtn.configure(image=self.play_image)
                self.playpausebtn.update_idletasks()
            elif (self.paused):
                mixer.music.unpause()
                self.paused = False
                self.waveform_label.configure(text=self.uilang["WaveformLabelPlaying"])
                self.playpausebtn.configure(image=self.pause_image)
                self.playpausebtn.update_idletasks()


    def play_audio(self):
        audio = pydub.AudioSegment.from_file(self.ttspath)
        self.audio_length = len(audio)
        del audio
        mixer.music.load(self.ttspath)
        mixer.music.play(loops = self.loops)
        self.seeker.configure(from_=0, to=self.audio_length-1)
        self.update_seeker()
        self.waveform_label.configure(text=self.uilang["WaveformLabelPlaying"])
        self.playpausebtn.configure(image=self.pause_image)
        self.playpausebtn.update_idletasks()


    def format_time(self, time_in_ms):
        ts = int(time_in_ms/1000)
        ts_string = str(ts)
        time_string = ""
        tmin = 0
        tmin_string = str(tmin)
        if (ts > 59):
            tmin = ts//60
            tmin_string = str(tmin)
            ts = ts%60
            ts_string = str(ts)
        if (len(str(ts)) == 1):
            ts_string = "0"+ts_string
        if (len(str(tmin)) == 1):
            tmin_string = "0"+tmin_string
        time_string = tmin_string+":"+ts_string
        return time_string
        
    def update_seeker(self):
        if (self.audio_playing()):
            audio_position = mixer.music.get_pos()
            if (audio_position >= self.audio_length):
                mixer.music.stop()
                if (self.loops == -1):
                    mixer.music.play(loops = self.loops)
                self.seeker.set(0)
                self.seeker.update_idletasks()
                self.seeker_timelabel.configure(text=self.format_time(0))
            else:
                self.seeker.set(audio_position)
                self.seeker.update_idletasks()
                self.seeker_timelabel.configure(text=self.format_time(audio_position))
            return self.after(10, self.update_seeker)
        else:
            self.seeker.set(0)
            self.seeker.update_idletasks()
            self.seeker_timelabel.configure(text=self.format_time(0))


    def reset_pause_state(self):
        if (not self.audio_playing()):
            self.paused = False
            self.playpausebtn.configure(image=self.play_image)
            self.playpausebtn.update_idletasks()
            if (self.waveform_label.cget('text') in (self.uilang["WaveformLabelGenerating"],
                                                    self.uilang["WaveformLabelNoTextAlert"],
                                                    self.uilang["WaveformLabelTTSNotGeneratedAlert"],
                                                    self.uilang["WaveformLabelNoConnectionAlert"],
                                                    self.uilang["WaveformLabelUnknownErrorAlert"])):
                return self.after (1000, lambda: (self.waveform_label.configure(text=self.uilang["WaveformLabelNormal"]), self.reset_pause_state()))
            self.waveform_label.configure(text=self.uilang["WaveformLabelNormal"])
        return self.after (50, self.reset_pause_state)


    def playpause_cb(self):
        text = self.textbox.get("1.0", tk.END).strip()
        if ((text != "" and self.text != text) or self.settings_changed or self.error_occured):
            self.error_occured = False
            self.settings_changed = False
            self.log("Generating TTS...")
            self.waveform_label.configure(text=self.uilang["WaveformLabelGenerating"])
            self.waveform_label.update()
            self.tts = ttsh.TTSHandler(text, api=self.config["APIInUse"])
            self.ttspath = USERDIR+DIRS_IN_USERDIR["CACHE"]+str(round(time.time()))
            if (self.config["APIInUse"] == "Pyttsx3"):
                self.tts.set_property(rate=int(self.config["Pyttsx3Speed"]), volume=float(self.config["Pyttsx3Volume"])/100, voice=int(self.config["Pyttsx3VoiceID"]))
                self.ttspath += ".wav"
            else:
                self.ttspath += ".mp3"
            try:
                self.tts.generate_tts(self.ttspath)
                while (True):
                    if (os.path.isfile(self.ttspath)):
                        if (os.path.getsize(self.ttspath) == 0):
                            pass
                        else:
                            break
            except ttsh.ttsexceptions.GTTSConnectionError as e:
                self.waveform_label.configure(text=self.uilang["WaveformLabelNoConnectionAlert"])
                self.waveform_label.update()
                self.error_occured = True
                self.log (e, logtype="ERROR")
            except:
                self.waveform_label.configure(text=self.uilang["WaveformLabelUnknownErrorAlert"])
                self.waveform_label.update()
                self.error_occured = True
            self.text = text

        if (text == ""):
            self.waveform_label.configure(text=self.uilang["WaveformLabelNoTextAlert"])
        if (os.path.isfile(self.ttspath) and not self.audio_playing() and text != "" and not self.error_occured):
            self.log ("Running TTS...")
            self.play_audio()
        else:
            self.pause_unpause_audio()


    def stop_cb(self):
        mixer.music.stop()
        self.seeker.set(0)
        self.seeker.update_idletasks()
        self.seeker_timelabel.configure(text=self.format_time(0))
        self.paused = False
        self.audio_length = 0
        self.waveform_label.configure(text=self.uilang["WaveformLabelNormal"])
        self.playpausebtn.configure(image=self.play_image)
        self.playpausebtn.update_idletasks()


    def save_cb(self):
        if (self.textbox.get("1.0", tk.END).strip() == "" or self.ttspath == ""):
            self.waveform_label.configure(text=self.uilang["WaveformLabelTTSNotGeneratedAlert"])
            return
        supported_formats = [
                                ("MP3 - Compressed audio", "*.mp3"),
                                ("WAV - High quality uncompressed audio", "*.wav"),
                                ("OGG Vorbis - Suitable for streaming", "*.ogg"),
                                ("FLAC", "*.flac"),
                                ("AAC", "*.aac"),
                                ("M4A", "*.m4a"),
                                ("WMA", "*.wma"),
                                ("AIFF", "*.aiff")
                            ]
        file_path = ""
        initialfilename = "Untitled Speech"
        tempname = initialfilename
        i=1
        for _file in os.listdir(self.config["LastSavedInDirectory"]):
            if (_file.startswith(initialfilename)):
                tempname = f"{initialfilename} ({i})"
                i+=1
        initialfilename = tempname
        try:
            if (system() == 'Windows'):
                file_path = tk.filedialog.asksaveasfilename(title=self.uilang["SaveDialogTitle"], initialfile=initialfilename, defaultextension=".mp3", filetypes=supported_formats, initialdir=self.config["LastSavedInDirectory"])
            else:
                file_path = tk.filedialog.asksaveasfilename(title=self.uilang["SaveDialogTitle"], initialfile=initialfilename, filetypes=supported_formats, initialdir=self.config["LastSavedInDirectory"])
        except:
            pass
        if (file_path != ""):
            self.config["LastSavedInDirectory"] = os.path.dirname(file_path)
            if (self.ttspath.endswith(".wav")):
                if (file_path.endswith(".wav")):
                    copy(self.ttspath, file_path)
                else:
                    audio = pydub.AudioSegment.from_wav(self.ttspath)
                    audio.export(file_path)
            elif (self.ttspath.endswith(".mp3")):
                if (file_path.endswith(".mp3")):
                    copy(self.ttspath, file_path)
                else:
                    audio = pydub.AudioSegment.from_mp3(self.ttspath)
                    audio.export(file_path)
            self.log("Audio saved successfully!")
            


    def volume_slider_cb(self, val):
        if (self.volume_slider.get() == 0):
            self.volume_icon.configure(image=ctk.CTkImage(self.volume_image_muted_original, size = self.volume_icon.cget('image').cget('size')))
        else:
            self.volume_icon.configure(image=ctk.CTkImage(self.volume_image_original, size = self.volume_icon.cget('image').cget('size')))
        mixer.music.set_volume(val/100)
        self.config["AudioVolume"] = str(int(val))


    def loop_cb(self):
        if (self.config["LoopAudio"] == "0"):
            self.loops = -1
            self.loopbtn.configure(fg_color='#9400ff')
            self.config["LoopAudio"] = "1"
        else:
            self.loops = 0
            self.loopbtn.configure(fg_color=self.accent_color)
            self.config["LoopAudio"] = "0"


    def volume_icon_cb(self):
        if (self.volume_slider.get() != 0):
            self.volume_slider.set(0)
            self.config["AudioVolume"] = "0"
            self.volume_icon.configure(image=ctk.CTkImage(self.volume_image_muted_original, size = self.volume_icon.cget('image').cget('size')))
        else:
            self.volume_slider.set(100)
            self.config["AudioVolume"] = "100"
            self.volume_icon.configure(image=ctk.CTkImage(self.volume_image_original, size = self.volume_icon.cget('image').cget('size')))
        self.volume_slider_cb(self.volume_slider.get())


    def show_about(self):
        self.about_window = tk.Toplevel(self)
        self.about_window.transient(self)
        self.about_window.title(self.uilang["AboutTitle"])
        self.about_window.dimensions = "480x360"

        # Get the height and width from the dimensions and center the toplevel on the master
        self.about_window.height = int(self.about_window.dimensions[self.about_window.dimensions.index('x')+1::])
        self.about_window.width = int(self.about_window.dimensions[0:self.about_window.dimensions.index('x')])
        center_x = int(self.winfo_rootx()+self.winfo_width()-self.about_window.width-self.winfo_width()/2+self.about_window.width/2)
        center_y = int(self.winfo_rooty()+self.winfo_height()-self.about_window.height-self.winfo_height()/2+self.about_window.height/2)

        if (center_x+self.about_window.width > self.winfo_screenwidth()):
            center_x = self.winfo_screenwidth() - self.about_window.width - 20
        if (center_y+self.about_window.height > self.winfo_screenheight()):
            center_y = self.winfo_screenheight() - self.about_window.height - 20
        if (center_x+self.about_window.width < self.winfo_width()//2):
            center_x = 20
        if (center_y+self.about_window.height < self.winfo_height()//2):
            center_y = 20   
        if (center_x < 0):
            center_x = int(self.winfo_screenwidth()/2 - self.about_window.width/2)
        if (center_y < 0):
            center_y = int(self.winfo_screenheight()/2 - self.about_window.height/2)

        self.about_window.geometry(self.about_window.dimensions+"+%d+%d"%(center_x, center_y))
        self.about_window.resizable(0,0)
        self.wait_visibility(self.about_window)
        self.about_window.grab_set()
        self.about_window.focus_set()
        self.about_icon = ctk.CTkImage(Image.open(ROOTDIR+"assets/toice.png"), size=(150, 150))
        self.about_image = ctk.CTkLabel(self.about_window, image=self.about_icon, text=None)
        self.about_image.pack(pady=15)
        self.about_text = tk.Label(self.about_window, text="Toice : A text to speech app\n\nVersion - 0.0.0_alpha (Unstable build)\n\nAUTHOR : Arijit Kumar Das <arijitkdgit.official@gmail.com>\n\nToice is a free software, you may distribute Toice under the terms\nof the GNU GPL v3. You should have received a copy of the LICENSE\nwith Toice. If not, check out the terms of GNU GPL v3 online.", font=(self.font[0], 10))
        self.about_text.pack(padx=15)


    def alter_textbox_placeholder(self):
        if (self.textbox.get("1.0", tk.END).strip('\n') != ""):
            self.textbox_placeholder.grid_forget()
        else:
            self.textbox_placeholder.grid(row=0, column=0, sticky=tk.NW, padx=15, pady=10)
        self.textbox_placeholder.update()
        return self.after(50, self.alter_textbox_placeholder)


    def add_widgets(self):

        # Adding the Text area
        self.textbox = ctk.CTkTextbox(self.background, font=self.font, border_width=3,
                                        border_color= '#5f00a4', corner_radius=10, wrap='word', fg_color='#1c1b22')
        self.textbox_placeholder = ctk.CTkLabel(self.textbox, text=self.uilang["TextboxPlaceholderLabel"], font=self.font, text_color='gray')
        self.textbox_placeholder.grid(row=0, column=0, sticky=tk.NW, padx=15, pady=10)
        self.background.create_window(20, 100, anchor=tk.NW, window=self.textbox)

        # Add a Settings button
        self.settingsbtn_icon = ctk.CTkImage(Image.open(ROOTDIR+"assets/settings.png"), size=(40, 40))
        self.aboutbtn_icon = ctk.CTkImage(Image.open(ROOTDIR+"assets/about.png"), size=(40, 40))

        self.tool_frame = ctk.CTkFrame(self.background, fg_color=self.accent_color)
        self.settingsbtn = ctk.CTkButton(self.tool_frame, image=self.settingsbtn_icon, text=None, command=self.show_settingsmenu, width=60, height=60,
                                        hover_color='#5f00a4', fg_color=self.accent_color, corner_radius=10)
        self.settingsbtn.pack(side=tk.RIGHT, padx=(10, 0))
        self.aboutbtn = ctk.CTkButton(self.tool_frame, image=self.aboutbtn_icon, text=None, command=self.show_about, width=60, height=60,
                                        hover_color='#5f00a4', fg_color=self.accent_color, corner_radius=10)
        self.aboutbtn.pack(side=tk.LEFT)
        self.tool_frame_canvasid = self.background.create_window(int(self.config["WindowWidth"])-20, 20, anchor=tk.NE, window=self.tool_frame)
        
        # Add a waveform image
        self.waveform_frame = ctk.CTkFrame(self.background,  fg_color='#1c1b22', border_width=3, border_color='#5f00a4', corner_radius=10)
        self.waveform_frame.pack_propagate(False)
        self.waveform_canvasid = self.background.create_window(int(self.config["WindowWidth"])-20, 100, anchor=tk.NE, window=self.waveform_frame)
        self.waveform_label = ctk.CTkLabel(self.waveform_frame, text=self.uilang["WaveformLabelNormal"], bg_color='#1c1b22', font=(self.font[0], 15))
        self.waveform_label.pack(expand=True, padx=3, pady=3)

        # Add a control panel
        self.control_frame = ctk.CTkFrame(self.background, fg_color=self.accent_color)
        self.control_frame.pack_propagate(False)
        self.control_canvasid = self.background.create_window(int(self.config["WindowWidth"])-20, int(self.config["WindowHeight"])-20, anchor=tk.SE, window=self.control_frame)

        # Add a seek slider in the control panel
        self.seeker_frame = ctk.CTkFrame(self.control_frame,  fg_color=self.accent_color)
        self.seeker_frame.pack(fill=tk.X, side=tk.TOP)
        self.seeker_timelabel = ctk.CTkLabel(self.seeker_frame, text="00:00", font=(self.font[0], 15))
        self.seeker_timelabel.pack(side=tk.RIGHT, padx=5)
        self.seeker = ctk.CTkSlider(self.seeker_frame, progress_color="#9400ff", fg_color='white', button_color="#9400ff", button_hover_color="#5f00a4", bg_color=self.control_frame.cget('bg_color'))
        self.seeker.pack(side=tk.LEFT, fill=tk.X, pady=30/1920*int(self.config["WindowWidth"]), padx=5)
        self.seeker.set(0)

        # Add play/pause and stop buttons
        self.button_frame = tk.Frame(self.control_frame, bg=self.control_frame.cget('bg_color'))
        self.button_frame.pack(fill=tk.X)

        self.play_image_original = Image.open(ROOTDIR+"assets/play.png")
        self.play_image = self.play_image_original
        self.play_image = ctk.CTkImage(self.play_image)

        self.pause_image_original = Image.open(ROOTDIR+"assets/pause.png")
        self.pause_image = self.pause_image_original
        self.pause_image = ctk.CTkImage(self.pause_image)

        self.stop_image_original = Image.open(ROOTDIR+"assets/stop.png")
        self.stop_image = self.stop_image_original
        self.stop_image = ctk.CTkImage(self.stop_image)

        self.loop_image_original = Image.open(ROOTDIR+"assets/loop.png")
        self.loop_image = self.loop_image_original
        self.loop_image = ctk.CTkImage(self.loop_image)

        self.save_image_original = Image.open(ROOTDIR+"assets/save.png")
        self.save_image = self.save_image_original
        self.save_image = ctk.CTkImage(self.save_image)

        self.volume_image_original = Image.open(ROOTDIR+"assets/volume-loud.png")
        self.volume_image = self.volume_image_original
        self.volume_image = ctk.CTkImage(self.volume_image)

        self.volume_image_muted_original = Image.open(ROOTDIR+"assets/volume-muted.png")
        self.volume_image_muted = self.volume_image_muted_original
        self.volume_image_muted = ctk.CTkImage(self.volume_image_muted)

        self.playpausebtn = ctk.CTkButton(self.button_frame, image=self.play_image, text=None, fg_color=self.accent_color, hover_color='#5f00a4', corner_radius=10, command=self.playpause_cb)
        self.playpausebtn.play_image = self.play_image
        self.playpausebtn.pause_image = self.pause_image
        self.playpausebtn.pack(side=tk.LEFT, anchor=tk.W)

        self.stopbtn = ctk.CTkButton(self.button_frame, image=self.stop_image, text=None, fg_color=self.accent_color, hover_color='#5f00a4', corner_radius=10, command=self.stop_cb)
        self.stopbtn.pack(side=tk.LEFT)
        self.stopbtn.image = self.stop_image

        self.loopbtn = ctk.CTkButton(self.button_frame, image=self.loop_image, text=None, fg_color=self.accent_color, hover_color='#5f00a4', corner_radius=10, command=self.loop_cb)
        if (self.config["LoopAudio"] == "1"):
            self.loopbtn.configure(fg_color='#9400ff')
        self.loopbtn.pack(side=tk.LEFT)
        self.loopbtn.image = self.loop_image

        self.savebtn = ctk.CTkButton(self.button_frame, image=self.save_image, text=None, fg_color=self.accent_color, hover_color='#5f00a4', corner_radius=10, command=self.save_cb)
        self.savebtn.pack(side=tk.RIGHT)
        self.savebtn.image = self.save_image

        self.volume_frame = ctk.CTkFrame(self.button_frame, fg_color=self.accent_color)
        self.volume_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.volume_icon = ctk.CTkButton(self.volume_frame, text=None, image=self.volume_image, fg_color=self.accent_color, hover_color='#5f00a4', command=self.volume_icon_cb)
        self.volume_icon.pack(side=tk.LEFT, padx=(0, 5), ipadx=1, ipady=1)
        self.volume_icon.image = self.volume_image
        self.volume_icon.image_muted = self.volume_image_muted

        self.volume_slider = ctk.CTkSlider(self.volume_frame, from_=0, to=100, progress_color="#9400ff", fg_color='white', button_color="#9400ff", button_hover_color="#5f00a4", bg_color=self.accent_color,
                                            command = self.volume_slider_cb)
        self.volume_slider.set(int(self.config["AudioVolume"]))
        mixer.music.set_volume(int(self.config["AudioVolume"])/100)
        self.volume_slider.pack(fill=tk.X, expand=True, side=tk.RIGHT)

        #self.waveform_label = tk.Label(self.waveform_frame, bg=self.accent_color)
        #self.waveform_label.pack(fill=tk.BOTH, expand=True, padx=1.5, pady=1.5)


    def log(self, string, end="\n", logtype="INFO"):
        if (self.logging == True):
            print (f"[{self.log_count}]:", f"{logtype}:", string, end=end)
            self.log_count += 1


    def get_default(self, datatype="config"):
        data = {}
        data_lines = []
        if (datatype == "config"): 
            data_lines = DEFAULT_CONFIG.split("\n")
        elif (datatype == "uilang"):
            data_lines = DEFAULT_UI_LANG.split("\n")

        for line in data_lines:
            if (line.find('=') != -1):
                key = line[:line.index('=')].strip()
                value = line[line.index('=')+1::].strip()
                data[key] = value
        return data
            


    def set_default(self, *settings, datatype="config"):
        if (datatype == "config"):
            for setting in settings:
                self.config[setting] = self.defcon[setting]
        elif (datatype == "uilang"):
            for setting in settings:
                self.config[setting] = self.defuilang[setting]


    def load_settings(self):
        self.log ("Loading user configuration data...")
        os.makedirs(USERDIR, exist_ok = True)
        for directory in DIRS_IN_USERDIR:
            os.makedirs(USERDIR+DIRS_IN_USERDIR[directory], exist_ok = True)
        if (not os.path.isfile(CONFIG_FILE)):
            self.log ("Detected first time run, creating user configuration file")
            with open(CONFIG_FILE, 'w') as configfile:
                configfile.write(DEFAULT_CONFIG)
            self.log ("User configuration file created")

        with open(CONFIG_FILE) as configfile:
            for line in configfile.readlines():
                if (not (line.startswith('//') or line.startswith('#')) and line.find('=') != -1):
                    key = line[:line.index('=')].strip()
                    value = line[line.index('=')+1::].strip()
                    self.config[key] = value

        # Verify configuration integrity
        for key in self.defcon.keys():
            try:
                if (key.startswith("Window") or key == "AudioVolume"):
                    self.config[key] = str(int(self.config[key]))
                    if (key == "WindowMaximized" and int(self.config[key]) not in (0, 1)):
                        raise ValueError
                elif (key == "LastSavedInDirectory"):
                    if (not os.path.isdir(self.config["LastSavedInDirectory"])):
                        raise ValueError
                elif (key == "APIInUse"):
                    if (self.config[key] not in ("Pyttsx3", "GTTS")):
                        raise ValueError
                elif (key == "LoopAudio"):
                    if (int(self.config[key]) not in (0, 1)):
                        raise ValueError
                elif (key.startswith("Textbox")):
                    tempwidget = tk.Text(foreground=self.config[key])
                    del tempwidget
                elif (key.startswith("Font")):
                    if (key == "FontSize"):
                        self.config[key] = str(int(self.config[key]))
                elif (key == "UILanguage"):
                    if (self.config[key] not in self.supported_ui_langs):
                        raise ValueError
                elif (key.startswith("Pyttsx3")):
                    if (key == "Pyttsx3Speed"):
                        val = int(self.config[key])
                        if (val>300 or val<50 or self.config[key].find('.') != -1):
                            raise ValueError
                    elif (key == "Pyttsx3Volume"):
                        val = int(self.config[key])
                        if (val>100 or val<0 or self.config[key].find('.') != -1):
                            raise ValueError
                    elif (key == "Pyttsx3VoiceID"):
                        if (int(self.config[key]) < 0 or self.config[key].find('.') != -1):
                            raise ValueError
                else:
                    self.config[key]
            except KeyError:
                self.log ("Missing value for "+key+", loading default value", logtype="ERROR")
                self.set_default(key)
            except:
                self.log ("Invalid value for "+key+", loading default value", logtype="ERROR")
                self.set_default(key)
        config_keys = list(self.config.keys())
        for key in config_keys:
            try:
                self.defcon[key]
            except KeyError as e:
                self.log ("Removing unwanted key: "+str(e))
                self.config.pop(key)
        self.log ("User configuration loaded")
        self.log (self.config)


    def save_settings(self):
        # Save window state
        if (self.maximize()):
            self.config["WindowMaximized"] = "1"
        else:
            self.config["WindowX"] = str(self.winfo_rootx()-(1 if self.winfo_rootx()>0 else 0))     # Adjust offset due tkinter's internal bug
            self.config["WindowY"] = str(self.winfo_rooty()-(30 if self.winfo_rooty()>0 else 0))    # Adjust offset due tkinter's internal bug
            self.config["WindowWidth"] = str(self.winfo_width())
            self.config["WindowHeight"] = str(self.winfo_height())
            self.config["WindowMaximized"] = "0"
                
        self.log (self.config)
        with open(CONFIG_FILE, 'w') as configfile:
            for key, value in self.config.items():
                configfile.write(key+" = "+value+"\n")


    def show_settingsmenu(self):
        # Running settings menu
        last_uilang = self.config["UILanguage"]
        self.log ("Running settings menu...")
        self.settingsmenu= ToiceSettingsMenu(self, self.config, self.uilang)
        self.settingsmenu.run()
        self.log ("Closed settings menu, loading saved settings")
        self.config = self.settingsmenu.config.copy()
        self.settings_changed = self.settingsmenu.settings_changed
        self.log ("Saved settings loaded")
        if (self.config["UILanguage"] != last_uilang):
            response = mbox.askyesno (APPNAME, self.uilang["UILanguageChangeAlert"])
            if (response == True):
                self.exit()
                logging = self.logging
                del self
                return start_toice(logging=logging)
        

        
    def load_ui_lang(self, lang, langfile):
        with open(langfile, encoding='UTF-8') as langpack:
            langpack_lines = langpack.readlines()
            for line in langpack_lines:
                if (line.find('=') != -1):
                    key = line[:line.index('=')].strip()
                    value = line[line.index('=')+1::].strip().replace("<BREAK>", "\n")
                    self.uilang[key] = value


    def reduce(self, n, percent):
        return (n-round(percent/100*n))


    def maximize(self, state=None):
        if (system() == "Windows"):
            if (state == True):
                self.state('zoomed')
                return True
            elif (state == False):
                self.state('normal')
                return False
            else:
                return self.state() == "zoomed"
        else:
            if (state == True):
                self.wm_attributes('-zoomed', int(state))
                return True
            elif (state == False):
                self.wm_attributes('-zoomed', int(state))
                return False
            else:
                return bool(self.wm_attributes('-zoomed'))


    def exit(self):
        self.log ("Saving settings...")
        self.save_settings()
        self.log ("Settings saved")

        if (system() != "Windows"):
            if (self.installed_font):
                self.log ("Noto Sans font was not previously installed, uninstalling it")
            else:
                self.log ("Noto Sans font was previously installed and will not be uninstalled")
            self.unload_notosans_font()

        self.log ("Exitting...")
        self.destroy()


    def load_bg_image(self, directory=ROOTDIR):

        cached_imgpath = USERDIR+DIRS_IN_USERDIR["CACHE"]+"CACHED_background.jpg"
        imgpath = directory+DIRS_IN_USERDIR["IMAGE"]+"background-default.jpg"

        if (os.path.isfile(cached_imgpath)):
            self.log ("Found cached background image, loading it")
            self.orig_image = Image.open(cached_imgpath)

            # Extract the accent color from the background image
            temp_img = self.orig_image.resize((150, 150))
            colors = temp_img.getcolors(temp_img.size[0] * temp_img.size[1])
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            self.dominant_color_rgb = sorted_colors[0][1]
            self.accent_color = self.get_color_code(self.dominant_color_rgb)

            status = SUCCESS

        elif (os.path.isfile(imgpath)):
            self.orig_image = Image.open(imgpath)

            # Resize the cached image by 40% to reduce cache-size
            cached_image = self.orig_image.resize((1920, 1080), Image.LANCZOS)

            # Apply Gaussian blur on original image
            self.orig_image = self.orig_image.filter(ImageFilter.GaussianBlur(50))

            # Apply 40% less Gaussian blur on cached image (this will save application of blur everytime the image is loaded from cache)
            cached_image = cached_image.filter(ImageFilter.GaussianBlur(15))

            # Extract the accent color from the background image
            temp_img = self.orig_image.resize((150, 150))
            colors = temp_img.getcolors(temp_img.size[0] * temp_img.size[1])
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            self.dominant_color_rgb = sorted_colors[0][1]
            self.accent_color = self.get_color_code(self.dominant_color_rgb)

            cached_image.save(cached_imgpath)
            self.log ("Cached background image was not found and has been generated")

            status = SUCCESS

        else:
            status = FAILURE

        # Apply to the background of window and canvas
        self.background.configure(bg=self.accent_color)
        self.configure(bg=self.accent_color)

        return status


    def get_complementory(self, rgb: tuple):

        r, g, b = rgb
        r_comp = 255-r
        g_comp = 255-g
        b_comp = 255-b
        return self.get_color_code((r_comp, g_comp, b_comp))


    def get_color_code(self, rgb: tuple):
        color_code = "#"
        for x in rgb:
            code = str(hex(x))[2::]
            color_code += code if len(code) == 2 else "0"+code
        return color_code


    def window_config(self, event):
        if (self.lastwinwidth != self.winfo_width() or self.lastwinheight != self.winfo_height()):
            if (self.orig_image is not None):
                self.bg_image = self.orig_image.resize((self.winfo_width(), self.winfo_height()), Image.NEAREST)
                self.tkbg_image = ImageTk.PhotoImage(self.bg_image)
                self.background.image = self.tkbg_image
                self.background.create_image(0, 0, anchor=tk.NW, image=self.background.image)

            if (self.textbox is not None):
                self.textbox.configure(width=round(400/800*self.winfo_width()), height=round(self.winfo_height()-120))

            if (self.tool_frame is not None):
                self.background.coords(self.tool_frame_canvasid, self.winfo_width()-20, 20)

            if (self.waveform_frame is not None):
                self.waveform_frame.configure(width=800/1920*int(self.winfo_width()), height=250/576*self.winfo_height())
                self.background.coords(self.waveform_canvasid, self.winfo_width()-20, 100)

            if (self.generatebtn_frame is not None):
                self.background.coords(self.generatebtn_canvasid, self.winfo_width()-self.waveform_frame.winfo_width()-20, self.winfo_height()-100)

            if (self.control_frame is not None):
                self.background.coords(self.control_canvasid, self.winfo_width()-20, self.winfo_height()-20)
                self.control_frame.configure(width=800/1920*self.winfo_width(), height=self.winfo_height()-self.waveform_frame.cget('height')-140)
                self.seeker.pack_configure(fill=tk.X, side=tk.TOP, pady=30/1920*self.winfo_height(), padx=5)

                #self.play_image = self.play_image_original.resize((round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())), Image.LANCZOS)
                self.play_image = ctk.CTkImage(self.play_image_original, size=(round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())))
                #self.pause_image = self.pause_image_original.resize((round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())), Image.LANCZOS)
                self.pause_image = ctk.CTkImage(self.pause_image_original, size=(round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())))
                if (self.playpausebtn.cget('image') == self.playpausebtn.play_image):
                    self.playpausebtn.configure(image=self.play_image, width=self.play_image.cget('size')[0], height=self.play_image.cget('size')[1])
                elif (self.playpausebtn.cget('image') == self.playpausebtn.pause_image):
                    self.playpausebtn.configure(image=self.pause_image, width=self.pause_image.cget('size')[0], height=self.pause_image.cget('size')[1])
                self.playpausebtn.pack_configure(ipadx=10/1920*self.winfo_width(), ipady=10/1080*self.winfo_height())
                self.playpausebtn.play_image = self.play_image
                self.playpausebtn.pause_image = self.pause_image


                #self.stop_image = self.stop_image_original.resize((round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())), Image.LANCZOS)
                self.stop_image = ctk.CTkImage(self.stop_image_original, size=(round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())))
                self.stopbtn.configure(image=self.stop_image, width=self.stop_image.cget('size')[0], height=self.stop_image.cget('size')[1])
                self.stopbtn.pack_configure(padx=0.0001/1920*self.winfo_width(), ipadx=10/1920*self.winfo_width(), ipady=10/1080*self.winfo_height())
                self.stopbtn.image = self.stop_image

                self.loop_image = ctk.CTkImage(self.loop_image_original, size=(round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())))
                self.loopbtn.configure(image=self.loop_image, width=self.loop_image.cget('size')[0], height=self.loop_image.cget('size')[1])
                self.loopbtn.pack_configure(ipadx=10/1920*self.winfo_width(), ipady=10/1080*self.winfo_height())
                self.loopbtn.image = self.loop_image

                self.save_image = ctk.CTkImage(self.save_image_original, size=(round(50/1080*self.winfo_height()), round(50/1080*self.winfo_height())))
                self.savebtn.configure(image=self.save_image, width=self.save_image.cget('size')[0], height=self.save_image.cget('size')[1])
                self.savebtn.pack_configure(ipadx=10/1920*self.winfo_width(), ipady=10/1080*self.winfo_height())
                self.savebtn.image = self.save_image

                if (self.volume_slider.get() != 0):
                    self.volume_image = ctk.CTkImage(self.volume_image_original, size=(round(40/1080*self.winfo_height()), round(40/1080*self.winfo_height())))
                    self.volume_icon.configure(image=self.volume_image, width=self.volume_image.cget('size')[0], height=self.volume_image.cget('size')[1])
                    self.volume_icon.image = self.volume_image
                else:
                    self.volume_image_muted = ctk.CTkImage(self.volume_image_muted_original, size=(round(40/1080*self.winfo_height()), round(40/1080*self.winfo_height())))
                    self.volume_icon.configure(image=self.volume_image_muted, width=self.volume_image_muted.cget('size')[0], height=self.volume_image_muted.cget('size')[1])
                    self.volume_icon.image_muted = self.volume_image_muted
                self.volume_frame.pack_configure(padx=20/1024*self.winfo_width())

            self.lastwinwidth = self.winfo_width()
            self.lastwinheight = self.winfo_height()


    def run(self):
        self.deiconify()
        self.bind("<Configure>", lambda event: self.after(10, self.window_config, event))
        self.bind("<FocusIn>", lambda event: self.textbox.focus_set())
        self.textbox.focus_set()
        self.reset_pause_state()
        self.alter_textbox_placeholder()
        self.mainloop()
        

def start_toice(logging=False):
    toice = Toice(logging=logging)
    toice.run()


if (__name__ == "__main__"):
    start_toice(logging=True)
