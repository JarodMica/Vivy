import os

from package import kokoro
from package import streamer
from utils import get_file_paths, get_personality_dir

# The only variables that need to be modifed
foldername = "streamer"
personality = "streamer"
attention_personality = "attention"
voicename = "Rem"
assistant_name = "Emi"
tts = "tortoise"
speech_recog = "whisper"

script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)
attention_dir = get_personality_dir(script_dir, attention_personality)

# Instantiate classes
_kokoro = kokoro.Kokoro(personality=personality_dir, 
                keys=keys, 
                save_folderpath=foldername_dir,
                voice_name=voicename,
                tts = tts,
                speech_recog = speech_recog
                )
attention_bot = kokoro.Kokoro(personality=attention_dir,
                              keys=keys,
                              save_folderpath=foldername_dir,
                              voice_name=voicename)

assistant = streamer.Streamer(_kokoro, attention_bot)

assistant.run(timeout=1, assistant_name=assistant_name)
