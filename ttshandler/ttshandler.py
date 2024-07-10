'''Defines the TTSHandler class'''

# External imports
import matplotlib.pyplot as plt 
import numpy as np 
import wave
import gtts
import pyttsx3
from pydub import AudioSegment
from tempfile import gettempdir
import time
from os import path

# Local import
from .ttsexceptions import *



class TTSHandler:

    def __init__(self, text, api, pyttsx3engine='default'):
        '''Initialize the TTSHandler class. -api must be either pyttsx3 or gtts (only these are supported). -text should be a string which will be converted into speech.
           An optional keyword argument -pyttsx3engine may be specified in case a non-default TTS engine is desired to be used. This option is ignored if api='gtts'.'''

        self.text = text
        self.gtts_tld = 'com'
        self.gtts_lang = 'en'
        self.gtts_slow = False
        self.output_file = None

        self.api = api.lower().strip()

        if (self.api == "pyttsx3"):
            if (pyttsx3engine == 'default'):
                try:
                    self.ttsengine = pyttsx3.init()
                except:
                    raise Pyttsx3InitializationError(f"Unable to initialize TTS engine for pyttsx3, probably no TTS engines are installed")
            else:
                try:
                    self.ttsengine = pyttsx3.init(pyttsx3engine)
                except:
                    raise Pyttsx3InitializationError(f"Unable to initialize TTS engine for pyttsx3, probably TTS engine '{pyttsx3engine}' is not installed or unsupported")
        elif (self.api == "gtts"):
            pass
        else:
            raise UnknownAPIError(f"Unknown TTS API: '{self.api}'")



    def set_tts_property(self, **properties):
        '''Set the speech properties.

           Pyttsx3 supported options are -rate, -volume and -voice.
           *    -rate --> an integer from 50 to 300 denoting the number of words per minute (default=150);
           *    -volume --> a float value from 0.0 to 1.0 that sets the volume of the speech (default=1.0);
           *    -voice --> an integer denoting the index of the voice as returned by engine.getProperty('voices') (default=0 [the first voice]).

           GTTS supported options are -tld, -lang and -slow
           *    -tld --> set the top-level domain used by GTTS for non-local accents (default='com' [local accent]);
           *    -lang --> set the language for TTS (default='en') [Both IETF language tags and language names are supported, but to avoid case-sensitivity issues use the IETF tags]
           *    -slow --> boolean to set whether the speech will be normal or slowed (default=False).

           For more details, refer to the respective documentations of Pyttsx3 or GTTS.'''        

        if (self.api == 'pyttsx3'):
            for _property in properties:
                if (_property == "rate" and (properties["rate"] not in range(50, 301) or type(properties["rate"]) is not int)):
                    raise TTSPropertyError(f"Invalid value for property -rate: '{properties[_property]}', must be an integer from 50 to 300")
                elif (_property == "volume" and (type(properties["volume"]) is str or (not 0 <= properties["volume"] <= 1.0))):
                    raise TTSPropertyError(f"Invalid value for property -rate: '{properties[_property]}', must be a float from 0.0 to 1.0")
                elif (_property == "voice"):
                    total_voices = len(self.ttsengine.getProperty('voices'))
                    invalid_flag_set = False
                    if (type(properties["voice"]) is not int):
                        invalid_flag_set = True
                    elif (properties["voice"] not in range(0, total_voices)):
                        if (properties["voice"] not in range(-total_voices, 0)):
                            invalid_flag_set = True
                    if (invalid_flag_set):
                        raise TTSPropertyError(f"Invalid value for property -voice: '{properties[_property]}', must be an integer index value from 0 to {total_voices-1} or from -{total_voices} to -1")
                else:
                    raise TTSPropertyError(f"Unknown property '-{_property}', must be one of -rate, -volume or -voice for pyttsx3")
            self.ttsengine.setProperty('rate', properties.get('rate', 150))
            self.ttsengine.setProperty('volume', properties.get('volume', 1.0))
            self.ttsengine.setProperty('voice', self.ttsengine.getProperty('voices')[properties.get('voice', 0)].id)

        elif (self.api == 'gtts'):
            for _property in properties:
                if (_property == 'lang'):
                    supported_langs = gtts.lang.tts_langs()
                    if (properties["lang"] not in supported_langs.keys()):
                        if (properties["lang"] in supported_langs.values()):
                            properties["lang"] = list(supported_langs.keys())[list(supported_langs.values()).index(properties["lang"])]
                        else:
                            raise TTSPropertyError("Unsupported GTTS language: '%s'"%properties["lang"])
                    else:
                        raise TTSPropertyError("Unsupported GTTS language: '%s'"%properties["lang"])
                elif (_property == 'slow' and properties['slow'] not in (1, 0, True, False)):
                    raise TTSPropertyError("-slow must have either a boolean True or boolean False value")
                elif (_property == 'tld' and type(properties['tld']) is not str):
                    raise TTSPropertyError(f"-tld must be a string, not a {type(properties['tld'])} value")
                else:
                    raise TTSPropertyError("Unknown property '-{_property}', must be one of -tld, -lang or -slow for gtts")
            self.gtts_tld = properties.get('tld', 'com')
            self.gtts_lang = properties.get('lang', 'en')
            self.gtts_slow = properties.get('slow', False)
        else:
            raise UnknownAPIError(f"Unknown TTS API: '{self.api}'")


    def generate_tts(self, output_file=''):
        '''Generate the TTS output. -output_file accepts an absolute file path for saving the TTS. Currently for api='pyttsx3' only WAV files are generated
           and for api='gtts' MP3 files are generated. This behaviour may be updated in the future for support of multiple audio file types.'''

        if (output_file == ''):
            output_file = path.join(gettempdir(), "temp%d"%int(time.time()))

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
            self.ttsengine = gtts.gTTS(text=self.text, lang=self.gtts_lang, tld=self.gtts_tld, slow=self.gtts_slow)
            try:
                self.ttsengine.save(output_file)
            except gtts.tts.gTTSError as gttserror:
                raise GTTSConnectionError(f"Failed to connect to GTTS. Message from API: \"{gttserror}\"")
            self.output_file = output_file

        else:
            raise UnknownAPIError(f"Unknown TTS API: '{self.api}'")


    def generate_waveform(self, output_file, **kwargs):
        '''Generate an pictorial wave form of the tts audio. -output_file accepts an absolute file path for saving the waveform as a PNG file. If the file has extension other
           than .png (case-insensitive), .png would be appended to the file and saved as PNG. Accepted keyword arguments are:
           *    -dimensions --> a string in the form of "<width>x<length>" specifying the dimensions of the output image (default="800x600");
           *    -fgcolor --> a color in RGBA format (eg: '#060e32') or any other valid color name that is recognized by matplotlib.pyplot (default='skyblue');
           *    -bgcolor --> same as -fgcolor (default='white').

           This function will raise a TTSNotGeneratedError if it is executed before running generate_tts().'''

        dimensions =  kwargs.get("dimensions", "800x600")
        fgcolor = kwargs.get("fgcolor", "skyblue")
        bgcolor = kwargs.get("bgcolor", "white")

        width = int(dimensions[0:dimensions.index("x")])
        height = int(dimensions[dimensions.index("x")+1::])

        if (self.output_file is None):
            raise TTSNotGeneratedError("Speech has not yet been synthesized, please run generate_tts() before attempting to get the speech waveform")
        else:
            if (self.api == 'pyttsx3'):
                audiofile = self.output_file
            elif (self.api == 'gtts'):
                try:
                    audio = AudioSegment.from_mp3(self.output_file)
                except FileNotFoundError:
                    raise NoFFmpegError("FFmpeg was not found on your system, get it from https://ffmpeg.org/download.html and add it to the system PATH variable")
                filename = "temp%d.mp3"%int(time())
                audiofile = path.join(gettempdir(), filename)
                audio.export(audiofile, format="wav")
                used_temp = True
            else:
                raise UnknownAPIError(f"Unknown TTS API: '{self.api}'")

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
        if (not output_file.lower().endswith('.png')):
            output_file += '.png'
        plt.savefig(output_file, bbox_inches='tight', pad_inches=0, facecolor = bgcolor)
        plt.close()
