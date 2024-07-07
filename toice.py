# -*- coding: utf8 -*-

# Background image by rawpixel.com on Freepik
# Link: https://www.freepik.com/free-vector/dark-gradient-background-with-copy-space_14731307.htm

# Gear icon on Settings button by rawpixel.com on Freepik
# Link: https://www.freepik.com/free-vector/illustration-cogwheel_2609999.htm

# Font used: Noto Sans


import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mbox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk, ImageFilter
import os
from shutil import copy
from subprocess import Popen, PIPE
from time import sleep
from platform import system
from settingsmenu import ToiceSettingsMenu

APPNAME = "Toice"

DIRS_IN_USERDIR = {
        "IMAGE": "images/",
        "CACHE": "cache/"
        }

DEFAULT_UI_LANG = \
'''
LanguageName = English (US)
TextboxPlaceholderLabel = Enter your text here...

SettingsMenuTitle = Preferences

GeneralTabName = General
GTTSTabName = GTTS
Pyttsx3TabName = Pyttsx3

Pyttsx3SpeedLabel = Speech Rate (Words per minute)
Pyttsx3VolumeLabel = Speech Volume (Percentage)
'''

ROOTDIR = os.path.dirname(__file__).replace("\\", "/")+"/"


if (system() == "Windows"):
    USERDIR = os.environ["LOCALAPPDATA"]+"\\"+APPNAME+"\\".replace("\\", "/")
elif (system() == "Darwin"):
    USERDIR = os.path.expanduser("~/Library/%s/"%APPNAME)
else:
    USERDIR = os.path.expanduser("~/.%s/"%APPNAME.lower())

CONFIG_FILE = USERDIR+"config.cfg"

DEFAULT_CONFIG = \
'''
WindowWidth = 800
WindowHeight = 600
WindowX = 50
WindowY = 50
WindowMaximized = 0

TextboxFG = black
TextboxBG = white

FontSize = 12

UILanguage = English (US)

Pyttsx3Speed = 150
Pyttsx3Volume = 67 
'''

SUCCESS = 0
FAILURE = 1


class Toice(tk.Tk):

    def __init__(self, logging=False):

        # Init super
        super().__init__()
        self.withdraw()

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
        self.accent_color = '#060e32'
        self.dominant_color_rgb = (6, 14 ,50)
        self.fg_color = self.get_complementory(self.dominant_color_rgb)
        self.defcon = self.get_default()
        self.defuilang = self.get_default(datatype="uilang")
        self.config = {}
        self.uilang = {}

        # Default widget values
        '[TEXTBOX]'
        self.textbox_frame = None

        '[SETTINGS BUTTON]'
        self.settingsbtn_frame = None
        self.settingsbtn_icon = None
        self.settingsbtn_text = None

        # Set app attributes
        self.title(APPNAME)
        self.minsize(800, 600)

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
            self.font = ('Segoe UI', int(self.config["FontSize"]))
        else:
            if (font_load_status == SUCCESS):
                self.log ("Detected Linux/MacOS system, Noto Sans font will be used for UI")
                self.font = ('Noto Sans', int(self.config["FontSize"]))
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
        self.background = tk.Canvas(self, highlightthickness=0)
        self.background.pack(fill=tk.BOTH, expand=True)

        # Load background
        if (self.load_bg_image() == SUCCESS):
            self.log ("Background image successfully loaded")
        else:
            self.log ("Failed to load background image (file probably missing)", logtype="ERROR")

        # Load ttk style
        self.ttk_style = ttk.Style()
        if (system() != "Windows"):
            self.ttk_style.theme_use('clam')

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


    def add_widgets(self):

        # Adding the Text area
        self.textbox_frame = tk.Frame(self.background, width=round(400/800*int(self.config["WindowWidth"])), height=int(self.config["WindowHeight"])-120, bg=self.fg_color)
        self.textbox_frame.pack_propagate(False)
        self.textbox = ScrolledText(self.textbox_frame, background=self.config['TextboxBG'], foreground=self.config['TextboxFG'], font=self.font, borderwidth=0, highlightthickness=0)
        self.textbox.pack(fill=tk.BOTH, expand=True, padx=1.5, pady=1.5)
        self.background.create_window(20, 100, anchor=tk.NW, window=self.textbox_frame)

        # Add a Settings button
        settings_icon = ROOTDIR+"assets/settings.png"
        try:
            self.settingsbtn_icon = ImageTk.PhotoImage(Image.open(settings_icon).resize((30, 30), Image.LANCZOS))
            self.log ("File %s loaded for settings button image"%(settings_icon))
        except FileNotFoundError:
            self.log ("File %s missing!"%(settings_icon), logtype="ERROR")
            self.log ("Defaulting to text instead of image for settings button")
            self.settingsbtn_text = "Settings"

        self.settingsbtn_frame = tk.Frame(self.background, bg=self.fg_color)
        self.settingsbtn = ttk.Button(self.settingsbtn_frame, text=self.settingsbtn_text, image=self.settingsbtn_icon, command=self.show_settingsmenu)
        self.settingsbtn.pack(fill=tk.BOTH, expand = True, padx=1.5, pady=1.5)
        if (system() == "Windows"):
            self.settingsbtn.pack_configure(ipadx=5, ipady=5)
        self.settingsbtn_canvasid = self.background.create_window(int(self.config["WindowWidth"])-20, 20, anchor=tk.NE, window=self.settingsbtn_frame)
        


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
                if (key.startswith("Window")):
                    int(self.config[key])
                elif (key.startswith("Textbox")):
                    tempwidget = tk.Text(foreground=self.config[key])
                    del tempwidget
                elif (key.startswith("Font")):
                    if (key == "FontSize"):
                        int(self.config[key])
                elif (key == "UILanguage"):
                    if (self.config[key] not in self.supported_ui_langs):
                        raise ValueError
                elif (key.startswith("Pyttsx3")):
                    if (key == "Pyttsx3Speed"):
                        int(self.config[key])
                        if (self.config[key]>300 or self.config[key]<50):
                            raise ValueError
                    elif (key == "Pyttsx3Volume"):
                        int(self.config[key])
                        if (self.config[key]>100 or self.config[key]<0):
                            raise ValueError
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
        self.settingsmenu= ToiceSettingsMenu(self, self.config, self.uilang)
        self.settingsmenu.run()
        

        
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

        cached_imgpath = USERDIR+DIRS_IN_USERDIR["CACHE"]+"CACHED_background-default.jpg"
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
            cached_image = self.orig_image.resize((self.reduce(self.orig_image.size[0], 40), self.reduce(self.orig_image.size[1], 40)), Image.LANCZOS)

            # Apply Gaussian blur on original image
            self.orig_image = self.orig_image.filter(ImageFilter.GaussianBlur(50))

            # Apply 40% less Gaussian blur on cached image (this will save application of blur everytime the image is loaded from cache)
            cached_image = cached_image.filter(ImageFilter.GaussianBlur(self.reduce(50, 40)))

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
        
        if (r < 255//2 or g < 255//2 or b < 255//2):
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0

            cmax = max(r_norm, g_norm, b_norm)
            cmin = min(r_norm, g_norm, b_norm)
            delta = cmax - cmin

            if delta == 0:
                hue = 0
            elif cmax == r_norm:
                hue = 60 * (((g_norm - b_norm) / delta) % 6)
            elif cmax == g_norm:
                hue = 60 * (((b_norm - r_norm) / delta) + 2)
            elif cmax == b_norm:
                hue = 60 * (((r_norm - g_norm) / delta) + 4)
            
            if (hue < 0):
                hue+=360

            # Calculate complementary hue
            complementary_hue = (hue + 180) % 360

            # Convert complementary HSV to RGB
            hi = int(complementary_hue / 60) % 6
            f = (complementary_hue / 60) - hi
            p = cmax * (1 - g_norm)
            q = cmax * (1 - (f * (1 - g_norm)))
            t = cmax * (1 - ((1 - f) * (1 - g_norm)))

            if (hi == 0):
                r_comp = cmax
                g_comp = t
                b_comp = p
            elif (hi == 1):
                r_comp = q
                g_comp = cmax
                b_comp = p
            elif (hi == 2):
                r_comp = p
                g_comp = cmax
                b_comp = t
            elif (hi == 3):
                r_comp = p
                g_comp = q
                b_comp = cmax
            elif (hi == 4):
                r_comp = t
                g_comp = p
                b_comp = cmax
            elif (hi == 5):
                r_comp = cmax
                g_comp = p
                b_comp = q

            # Convert to 0-255 range
            r_comp = int(r_comp * 255)
            g_comp = int(g_comp * 255)
            b_comp = int(b_comp * 255)

        else:
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

            if (self.textbox_frame is not None):
                self.textbox_frame.configure(width=round(400/800*self.winfo_width()), height=round(self.winfo_height()-120))

            if (self.settingsbtn_frame is not None):
                self.background.coords(self.settingsbtn_canvasid, self.winfo_width()-20, 20)
            self.lastwinwidth = self.winfo_width()
            self.lastwinheight = self.winfo_height()


    def run(self):
        self.deiconify()
        self.bind("<Configure>", self.window_config)
        self.textbox.focus_set()
        self.mainloop()
        

if (__name__ == "__main__"):
    toice = Toice(logging=True)
    toice.run()
