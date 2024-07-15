# -*- coding: utf8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from platform import system

class ToiceSettingsMenu(tk.Toplevel):

    def __init__(self, master: tk.Tk, settings_data: dict, lang_data: dict):

        super().__init__(master)

        self.config = settings_data.copy()
        self.master_config = settings_data.copy()
        self.uilang = lang_data

        self.transient(master)
        self.title(self.uilang["SettingsMenuTitle"]+" - "+self.master.title())

        self.dimensions = "480x360"
        self.settings_changed = False

        # Get the height and width from the dimensions and center the toplevel on the master
        self.height = int(self.dimensions[self.dimensions.index('x')+1::])
        self.width = int(self.dimensions[0:self.dimensions.index('x')])
        center_x = int(self.master.winfo_rootx()+self.master.winfo_width()-self.width-self.master.winfo_width()/2+self.width/2)
        center_y = int(self.master.winfo_rooty()+self.master.winfo_height()-self.height-self.master.winfo_height()/2+self.height/2)

        if (center_x+self.width > self.winfo_screenwidth()):
            center_x = self.winfo_screenwidth() - self.width - 20
        if (center_y+self.height > self.winfo_screenheight()):
            center_y = self.winfo_screenheight() - self.height - 20
        if (center_x+self.width < self.master.winfo_width()//2):
            center_x = 20
        if (center_y+self.height < self.master.winfo_height()//2):
            center_y = 20   
        if (center_x < 0):
            center_x = int(self.master.winfo_screenwidth()/2 - self.width/2)
        if (center_y < 0):
            center_y = int(self.master.winfo_screenheight()/2 - self.height/2)

        self.geometry(self.dimensions+"+%d+%d"%(center_x, center_y))
        self.resizable(0,0)

        try:
            import pyttsx3
            self.tts = pyttsx3.init()
        except:
            self.tts = None

        self.style = ttk.Style()

        if (system() != "Windows"):
            self.style.theme_use('clam')

        self.add_widgets()


    def add_widgets(self):

        padding = "         "

        self.tabbed_ui = ttk.Notebook(self)
        self.tabbed_ui.pack(fill=tk.BOTH)

        self.general_tab = ttk.Frame(self.tabbed_ui)
        self.add_general_widgets()

        self.gtts_tab = ttk.Frame(self.tabbed_ui)
        self.add_gtts_widgets()

        self.pyttsx3_tab = ttk.Frame(self.tabbed_ui)
        self.add_pyttsx3_widgets()

        # Add the frames to the Notebook as tabs
        self.tabbed_ui.add(self.general_tab, text=padding+self.uilang["GeneralTabName"]+padding)
        self.tabbed_ui.add(self.pyttsx3_tab, text=padding+self.uilang["Pyttsx3TabName"]+padding)
        self.tabbed_ui.add(self.gtts_tab, text=padding+self.uilang["GTTSTabName"]+padding)

        self.choose_api_frame = tk.Frame(self)
        self.choose_api_frame.pack(fill=tk.X, pady=(30, 10), padx=10)
        self.choose_api_label = tk.Label(self.choose_api_frame, text=self.uilang["ChooseAPILabel"]+":")
        self.choose_api_label.pack(side=tk.LEFT, padx=5)

        self.choose_api_var = tk.StringVar()
        self.choose_api_radiobutton_gtts = ttk.Radiobutton(self.choose_api_frame, text="GTTS", value="GTTS", variable=self.choose_api_var)
        self.choose_api_radiobutton_gtts.pack(side=tk.RIGHT, padx=20)
        self.choose_api_radiobutton_pyttsx3 = ttk.Radiobutton(self.choose_api_frame, text="Pyttsx3", value="Pyttsx3", variable=self.choose_api_var)
        self.choose_api_radiobutton_pyttsx3.pack(side=tk.RIGHT, padx=20)
        self.choose_api_var.set(self.config['APIInUse'])

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(fill=tk.X, pady=20, padx=10)
        self.apply_button = ttk.Button(self.buttons_frame, text=self.uilang["ButtonApply"], command = self.save_settings)
        self.cancel_button = ttk.Button(self.buttons_frame, text=self.uilang["ButtonCancel"], command = self.exit)
        self.ok_button = ttk.Button(self.buttons_frame, text=self.uilang["ButtonOK"], command = lambda: self.save_settings(close=True))
        self.apply_button.pack(side=tk.RIGHT, padx=(5, 10))
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        self.ok_button.pack(side=tk.RIGHT, padx=(10, 5))
        self.ok_button.bind("<Return>", lambda event: self.save_settings(close=True))
        self.cancel_button.bind("<Return>", lambda event: self.exit())
        self.apply_button.bind("<Return>", lambda event: self.save_settings())


    def add_general_widgets(self):
        self.general_label = ttk.Label(self.general_tab, text="Settings for this tab have not yet been added,\nPlease see the other tabs.")
        self.general_label.pack(expand=True)


    def add_gtts_widgets(self):
        self.gtts_label = ttk.Label(self.gtts_tab, text="Settings for this tab have not yet been added,\nPlease see the other tabs.")
        self.gtts_label.pack(expand=True)


    def add_pyttsx3_widgets(self):
        self.pyttsx3_speed_frame = tk.Frame(self.pyttsx3_tab)
        self.pyttsx3_speed_frame.pack(fill=tk.X, padx=5, pady=(30, 20))
        self.pyttsx3_speed_label = tk.Label(self.pyttsx3_speed_frame, text=self.uilang["Pyttsx3SpeedLabel"]+":")
        self.pyttsx3_speed_label.pack(side=tk.LEFT)
        self.pyttsx3_speed_var = tk.IntVar()
        self.pyttsx3_speed_slider = ttk.Scale(
                                            self.pyttsx3_speed_frame,
                                            from_ = 50,
                                            to_ = 300,
                                            orient = tk.HORIZONTAL,
                                            variable = self.pyttsx3_speed_var,
                                            command = lambda x: self.pyttsx3_speed_valuelabel.configure(text=self.add_numerical_padding(self.pyttsx3_speed_var.get()))
                                            )
        self.pyttsx3_speed_valuelabel = tk.Label(
                                        self.pyttsx3_speed_frame,
                                        text=self.add_numerical_padding(self.pyttsx3_speed_var.get())
                                        )
        self.pyttsx3_speed_valuelabel.pack(side=tk.RIGHT, padx=10)
        self.pyttsx3_speed_slider.pack(side=tk.RIGHT)
        self.pyttsx3_speed_slider.set(self.config["Pyttsx3Speed"])
        self.pyttsx3_speed_slider.bind("<Button-1>", lambda event: event.widget.focus_set())


        self.pyttsx3_volume_frame = tk.Frame(self.pyttsx3_tab)
        self.pyttsx3_volume_frame.pack(fill=tk.X, padx=5, pady=10)
        self.pyttsx3_volume_label = tk.Label(self.pyttsx3_volume_frame, text=self.uilang["Pyttsx3VolumeLabel"]+":")
        self.pyttsx3_volume_label.pack(side=tk.LEFT)
        self.pyttsx3_volume_var = tk.IntVar()
        self.pyttsx3_volume_slider = ttk.Scale(
                                            self.pyttsx3_volume_frame,
                                            from_ = 0,
                                            to_ = 100,
                                            orient = tk.HORIZONTAL,
                                            variable = self.pyttsx3_volume_var,
                                            command = lambda x: self.pyttsx3_volume_valuelabel.configure(text=self.add_numerical_padding(self.pyttsx3_volume_var.get()))
                                            )
        self.pyttsx3_volume_valuelabel = tk.Label(
                                        self.pyttsx3_volume_frame,
                                        text=self.add_numerical_padding(self.pyttsx3_volume_var.get())
                                        )
        self.pyttsx3_volume_valuelabel.pack(side=tk.RIGHT, padx=10)
        self.pyttsx3_volume_slider.pack(side=tk.RIGHT)
        self.pyttsx3_volume_slider.set(self.config["Pyttsx3Volume"])
        self.pyttsx3_volume_slider.bind("<Button-1>", lambda event: event.widget.focus_set())


        self.pyttsx3_voice_frame = tk.Frame(self.pyttsx3_tab)
        self.pyttsx3_voice_frame.pack(fill=tk.X, padx=5, pady=10)
        self.pyttsx3_voice_label = tk.Label(self.pyttsx3_voice_frame, text=self.uilang["Pyttsx3VoiceLabel"]+":")
        self.pyttsx3_voice_label.pack(side=tk.LEFT)
        self.pyttsx3_supported_voices = self.get_pyttsx3_supported_voices()
        self.pyttsx3_voice_combobox = ttk.Combobox(self.pyttsx3_voice_frame, values=self.pyttsx3_supported_voices, state='readonly')
        voice_gender = "Unknown"
        try:
            self.pyttsx3_voice_combobox.configure(width=max([len(voice_name) for voice_name in self.pyttsx3_supported_voices]))
            self.pyttsx3_voice_combobox.set(self.pyttsx3_supported_voices[int(self.config["Pyttsx3VoiceID"])])
            voice_gender = self.get_pyttsx3_voice_supported_gender(int(self.config["Pyttsx3VoiceID"]))
        except IndexError:
            self.pyttsx3_voice_combobox.set(self.pyttsx3_supported_voices[0])
        except ValueError:
            self.pyttsx3_voice_combobox.configure(state=tk.DISABLED, width=len(self.uilang["Pyttsx3NoVoiceError"]))
            self.pyttsx3_voice_combobox.set(self.uilang["Pyttsx3NoVoiceError"])

        self.pyttsx3_voice_combobox.pack (padx=10, side=tk.RIGHT)
        self.pyttsx3_voice_combobox.bind("<FocusIn>", lambda event: event.widget.selection_clear())
        self.pyttsx3_voice_combobox.bind("<<ComboboxSelected>>", lambda event:
        self.pyttsx3_voiceinfo_genderlabel.configure(text=self.uilang["Pyttsx3VoiceGender"+self.get_pyttsx3_voice_supported_gender(self.get_selected_voiceid())]))
        
        self.pyttsx3_voiceinfo_frame = tk.Frame(self.pyttsx3_tab)
        self.pyttsx3_voiceinfo_frame.pack(fill=tk.X, padx=5, pady=10)
        self.pyttsx3_voiceinfo_label = tk.Label(self.pyttsx3_voiceinfo_frame, text=self.uilang["Pyttsx3VoiceinfoLabel"]+":")
        self.pyttsx3_voiceinfo_label.pack(side=tk.LEFT)
        self.pyttsx3_voiceinfo_genderlabel = tk.Label(self.pyttsx3_voiceinfo_frame, text=self.uilang["Pyttsx3VoiceGender"+voice_gender])
        self.pyttsx3_voiceinfo_genderlabel.pack(side=tk.RIGHT, padx=10)
        


    def get_pyttsx3_voice_supported_gender(self, voiceid):
        voices = self.tts.getProperty('voices')
        gender = voices[voiceid].gender
        gender = str(gender).strip()
        if (gender.lower() not in ('male', 'female')):
            gender = "Unknown"
        return gender.capitalize()


    def get_pyttsx3_supported_voices(self):
        supported_voices = []
        if (self.tts is not None):
            voices = self.tts.getProperty('voices')
            for voice in voices:
                supported_voices.append(str(voice.name))
        return supported_voices


    def get_selected_voiceid(self):
        voices = self.tts.getProperty('voices')
        selected_voice_name = self.pyttsx3_voice_combobox.get()
        voiceid = 0
        for voice in voices:
            if (voice.name == selected_voice_name):
                gender = self.get_pyttsx3_voice_supported_gender(voiceid)
                break
            voiceid += 1
        return voiceid

        
                

    def add_numerical_padding(self, n, maxdigits=3, padding="  "):
        n = str(n)
        temppadding = "$"
        while (len(n) < maxdigits):
            n = temppadding+n
        return n.replace(temppadding, padding)


    def save_settings(self, close=False):
        self.config["Pyttsx3Speed"] = str(self.pyttsx3_speed_var.get())
        self.config["Pyttsx3Volume"] = str(self.pyttsx3_volume_var.get())
        self.config["Pyttsx3VoiceID"] = str(self.get_selected_voiceid())
        self.config["APIInUse"] = self.choose_api_var.get()
        if (self.config != self.master_config):
            print ("settings changed")
            self.settings_changed = True
        if (close):
            self.exit()

    def exit(self):
        self.destroy()
        
    def run(self):
        self.ok_button.focus_set()
        self.ok_button.configure(state=tk.ACTIVE)
        self.wait_visibility(self)
        self.grab_set()
        self.master.wait_window(self)

