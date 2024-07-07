# -*- coding: utf8 -*-

import tkinter as tk
import tkinter.ttk as ttk

class ToiceSettingsMenu(tk.Toplevel):

    def __init__(self, master: tk.Tk, settings_data: dict, lang_data: dict):

        super().__init__(master)

        self.config = settings_data
        self.uilang = lang_data

        self.transient(master)
        self.title(self.uilang["SettingsMenuTitle"]+" - "+self.master.title())

        self.dimensions = "400x480"

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

        self.add_widgets()


    def add_widgets(self):

        padding = "         "

        self.tabbed_ui = ttk.Notebook(self)
        self.tabbed_ui.pack(fill=tk.BOTH, expand=True)

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


    def add_general_widgets(self):
        self.general_label = ttk.Label(self.general_tab, text="Settings for this tab have not yet been added,\nPlease see the other tabs.")
        self.general_label.pack(expand=True)


    def add_gtts_widgets(self):
        pass


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
        

    def add_numerical_padding(self, n, maxdigits=3, padding="  "):
        n = str(n)
        temppadding = "$"
        while (len(n) < maxdigits):
            n = temppadding+n
        return n.replace(temppadding, padding)


    def run(self):
        self.focus_set()
        self.grab_set()
        self.master.wait_window(self)
