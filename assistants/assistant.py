import os

from package import kokoro
from package import assistant
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "assistant"
personality = "assistant"
voicename = "Rem"
tts = "default"
speech_recog = "whisper"

# Got rid of the pyinstaller block to determine whether it's an exe or not due to issues

script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir, personality_dir, keys = get_file_paths(script_dir, foldername, personality)

# Initialize the chat assitant with the variables that you've set 

_kokoro = kokoro.Kokoro(personality=personality_dir, 
                keys=keys, 
                save_folderpath=foldername_dir,
                voice_name=voicename,
                tts=tts,
                speech_recog=speech_recog
                )

assistant_ = assistant.Assistant(_kokoro)

assistant_.run()