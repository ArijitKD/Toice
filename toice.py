# Background image by rawpixel.com on Freepik
# Link: https://www.freepik.com/free-vector/dark-gradient-background-with-copy-space_14731307.htm

# Font used: Selawik
# Copyright 2015, Microsoft Corporation (License: SIL OPEN FONT LICENSE Version 1.1; License file: fonts/LICENSE.txt)
# Selawik is a trademark of Microsoft Corporation in the United States and/or other countries.


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

APPNAME = "Toice"
DEFAULT_UI_LANG = 'en-us'
DIRS = {
        "IMAGE": "images/",
        "LANGUAGE": "languages/",
        "CACHE": "cache/"
        }
ROOTDIR = "./"

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
'''

SUCCESS = 0
FAILURE = 1


class Toice(tk.Tk):

    def __init__(self, logging=False):

        # Init super
        super().__init__()
        self.withdraw()

        # Keep track of whether the Selawik font is being installed
        self.installed_font = False

        # Font files
        self.font_file = os.path.join(os.path.dirname(__file__), "fonts/selawk.ttf")
        self.font_file_linux = os.path.expanduser("~/.local/share/fonts/selawk.ttf")
        self.font_file_macos = os.path.expanduser("~/Library/Fonts/selawk.ttf")

        # Selawik font will be loaded for Linux/MacOS systems
        font_load_status = self.load_selawik_font()

        # Default values
        self.logging = logging
        self.log_count = 1
        self.orig_image = None
        self.bg_image = None
        self.tkbg_image = None
        self.accent_color = '#060e32'
        self.dominant_color_rgb = (6, 14 ,50)
        self.fg_color = self.get_complementory(self.dominant_color_rgb)
        self.defcon = self.get_default_config()

        # Default widget values
        self.textbox_frame = None

        # Set app attributes
        self.title(APPNAME)
        self.minsize(800, 600)

        # Set exit protocol
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # Load configuration settings
        self.load_settings()

        # Set the UI font
        if (system() == "Windows"):
            self.log ("Detected Windows system, Segoe UI font will be used for UI")
            self.font = ('Segoe UI', int(self.config["FontSize"]))
        else:
            if (font_load_status == SUCCESS):
                self.log ("Detected Linux/MacOS system, Selawik font will be used for UI")
                self.font = ('Selawik', int(self.config["FontSize"]))
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
            self.log ("Could not load background image")

        # Add the widgets
        self.add_widgets()


    def load_selawik_font(self):
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


    def unload_selawik_font(self):
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
        self.textbox_frame = tk.Frame(self.background, width=400/800*int(self.config["WindowWidth"]), height=480/600*int(self.config["WindowHeight"]), bg=self.fg_color)
        self.textbox_frame.pack_propagate(False)
        self.textbox = ScrolledText(self.textbox_frame, background=self.config['TextboxBG'], foreground=self.config['TextboxFG'], font=self.font, borderwidth=0, highlightthickness=0)
        self.textbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.background.create_window(20, 100, anchor=tk.NW, window=self.textbox_frame)
        #self.textbox_frame.pack()


    def log(self, string, end="\n", logtype="INFO"):
        if (self.logging == True):
            print (f"[{self.log_count}]:", f"{logtype}:", string, end=end)
            self.log_count += 1


    def get_default_config(self):
        config = {}
        config_lines = DEFAULT_CONFIG.split("\n")
        for line in config_lines:
            if (line.find('=') != -1):
                key = line[:line.index('=')].strip()
                value = line[line.index('=')+1::].strip()
                config[key] = value
        return config


    def set_default(self, *settings):
        for setting in settings:
            self.config[setting] = self.defcon[setting]


    def load_settings(self):
        self.log ("Loading user configuration data...")
        os.makedirs(USERDIR, exist_ok = True)
        for directory in DIRS:
            os.makedirs(USERDIR+DIRS[directory], exist_ok = True)
        if (not os.path.isfile(CONFIG_FILE)):
            self.log ("Detected first time run, creating user configuration file")
            with open(CONFIG_FILE, 'w') as configfile:
                configfile.write(DEFAULT_CONFIG)
            self.log ("User configuration file created")

        self.config = {}
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
        

        
    def load_ui_lang(self, lang_pack):
        pass


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
                self.log ("Selawik font was not previously installed, uninstalling it")
            else:
                self.log ("Selawik font was previously installed and will not be uninstalled")
            self.unload_selawik_font()

        self.log ("Exitting...")
        self.destroy()


    def load_bg_image(self, directory=ROOTDIR):

        cached_imgpath = USERDIR+DIRS["CACHE"]+"CACHED_background-default.jpg"
        imgpath = directory+DIRS["IMAGE"]+"background-default.jpg"

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
        if (self.orig_image is not None):
            self.bg_image = self.orig_image.resize((self.winfo_width(), self.winfo_height()), Image.NEAREST)
            self.tkbg_image = ImageTk.PhotoImage(self.bg_image)
            self.background.image = self.tkbg_image
            self.background.create_image(0, 0, anchor=tk.NW, image=self.background.image)

        if (self.textbox_frame is not None):
            self.textbox_frame.configure(width=round(400/800*self.winfo_width()), height=round(480/600*self.winfo_height()))


    def run(self):
        self.deiconify()
        self.bind("<Configure>", self.window_config)
        self.mainloop()
        

if (__name__ == "__main__"):
    toice = Toice(logging=True)
    toice.run()
