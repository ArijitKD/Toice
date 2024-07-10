'''Exception that are raised from the TTSHandler class are defined here.'''



class UnknownAPIError(Exception):
    '''Raised when the API specified while initializing TTSHandler is not one of \'pyttsx3\' or \'gtts\''''
    def __init__(self, message=""):
        super().__init__(message)



class TTSPropertyError(Exception):
    '''Raised while attempting to set an invalid or unsupported property for an initialized API'''
    def __init__(self, message=""):
        super().__init__(message)



class TTSNotGeneratedError(Exception):
    '''Raised when attempting to generate a speech waveform before the TTS has been generated'''
    def __init__(self, message=""):
        super().__init__(message)



class GTTSConnectionError(Exception):
    '''Raised when gtts.tts.GTTSError is raised'''
    def __init__(self, message=""):
        super().__init__(message)



class Pyttsx3InitializationError(Exception):
    '''Raised when the Pyttsx3 could not initialize the specified TTS engine'''
    def __init__(self, message=""):
        super().__init__(message)



class NoFFmpegError(Exception):
    '''Raised when FFmpeg is not installed, which is required for audio format conversions'''
    def __init__(self, message=""):
        super().__init__(message)
