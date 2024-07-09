import matplotlib.pyplot as plt 
import numpy as np 
import wave
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
from tempfile import gettempdir
from time import time
from os import path



class UnknownAPIError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSPropertyError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSNotGeneratedError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSHandler:

    def __init__(self, text, api):

        self.text = text
        self.gtts_tld = 'com'
        self.gtts_lang = 'en'
        self.gtts_slow = False
        self.output_file = None

        if (api.lower().strip() == "pyttsx3"):
            self.ttsengine = pyttsx3.init()
        elif (api.lower().strip() == "gtts"):
            pass
        else:
            raise UnknownAPIError("Unknown TTS API: '%s'"%api)

        self.api = api.lower().strip()


    def set_tts_property(self, **properties):

        if (self.api == 'pyttsx3'):
            self.ttsengine.setProperty('rate', properties.get('rate', 150))
            self.ttsengine.setProperty('volume', properties.get('volume', 1.0))
            self.ttsengine.setProperty('voice', self.ttsengine.getProperty('voices')[properties.get('voice', 0)].id)
        elif (self.api == 'gtts'):
            self.gtts_tld = properties.get('tld', 'com')
            self.gtts_lang = properties.get('lang', 'en')
            self.gtts_slow = properties.get('slow', False)
        else:
            raise TTSPropertyError(f"Cannot set property on API '{self.api}' (not supported)")


    def generate_tts(self, output_file=path.join(gettempdir(), "temp%d"%int(time()))):

        if (self.api == 'pyttsx3'):
            if (not output_file.lower().endswith('.wav')):
                output_file += ".wav"
            self.ttsengine.startLoop(False)
            self.ttsengine.save_to_file(self.text, output_file)
            self.ttsengine.iterate()
            self.ttsengine.endLoop()
            self.output_file = output_file

        elif (self.api == 'gtts'):
            if (not output_file.lower().endswith('.mp3')):
                output_file += ".mp3"
            self.ttsengine = gTTS(text=self.text, lang=self.gtts_lang, tld=self.gtts_tld, slow=self.gtts_slow)
            self.ttsengine.save(output_file)
            self.output_file = output_file

        else:
            raise UnknownAPIError("Failed to get TTS from API: '%s (not supported)'"%api)


    def get_tts_audio_graph(self, graph_save_path, **kwargs):

        dimensions =  kwargs.get("dimensions", "800x600")
        fgcolor = kwargs.get("fgcolor", "skyblue")
        bgcolor = kwargs.get("bgcolor", "white")

        width = int(dimensions[0:dimensions.index("x")])
        height = int(dimensions[dimensions.index("x")+1::])

        if (self.output_file is None):
            raise TTSNotGeneratedError("Speech has not yet been synthesized, please run generate_tts() before attempting to get the audio graph")
        else:
            if (self.api == 'pyttsx3'):
                audiofile = self.output_file
            elif (self.api == 'gtts'):
                audio = AudioSegment.from_mp3(self.output_file)
                filename = "temp%d.mp3"%int(time())
                audiofile = path.join(gettempdir(), filename)
                audio.export(audiofile, format="wav")
                used_temp = True
            else:
                raise UnknownAPIError("Failed to get TTS audio graph from API: '%s (not supported)'"%api)

        audiodata = wave.open(audiofile)

        signal = audiodata.readframes(-1)
        signal = np.frombuffer(signal, dtype ="int16")

        f_rate = audiodata.getframerate()
        t = np.linspace(0, len(signal)/f_rate, num=len(signal))

        plt.figure(1, figsize=(width/100, height/100))
        plt.axis('off')
        plt.margins(x=0, y=0)

        plt.plot(t, signal, color=fgcolor)
            
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        plt.savefig(graph_save_path, bbox_inches='tight', pad_inches=0, facecolor = bgcolor)
        plt.close()
