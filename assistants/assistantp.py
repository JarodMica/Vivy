import os

from package import kokoro
from package import assistant_p
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "assistantP"
personality = "assistantP"
voicename = "Rem"
tts = "system"
speech_recog = "whisper"

# removed the block here that was meant for a pyinstaller exe due to the exe files not working properly

script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)

_kokoro = kokoro.Kokoro(personality=personality_dir, 
                keys=keys, 
                save_folderpath=foldername_dir,
                voice_name=voicename,
                tts=tts,
                speech_recog=speech_recog
                )

assistant = assistant_p.AssistantP(_kokoro)
assistant.run()
