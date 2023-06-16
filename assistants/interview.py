import os

from package import kokoro
from package import interview
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "interview"
personality = "interview"
voicename = "Rem"
tts = "system"
speech_recog = "whisper"

script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)

_kokoro = kokoro.Kokoro(personality=personality_dir, 
                  keys=keys,
                  save_folderpath=foldername_dir,
                  voice_name=voicename,
                  tts = tts,
                  speech_recog = speech_recog
                  )
assistant = interview.Interview(_kokoro)

assistant.run()

