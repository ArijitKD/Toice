class UnknownAPIError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSPropertyError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSNotGeneratedError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSConnectionError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class TTSEngineInitializationError(Exception):
    def __init__(self, message=""):
        super().__init__(message)



class NoFFmpegError(Exception):
    def __init__(self, message=""):
        super().__init__(message)