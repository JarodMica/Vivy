import sys 
import os

from package import kokoro
from package import streamer
from utils import get_file_paths, get_personality_dir

# The only variables that need to be modifed
foldername = "streamer"
personality = "streamer"
attention_personality = "attention"
voicename = "Rem"
useEL = True
usewhisper = True

# This code block only checks if it's being ran as a python script or as an exe
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
    while True:
        user_input = input("Are you using an Eleven Labs voice (yes/no)?\n")
        if user_input == 'yes':
            voicename = input("What is the name of you Eleven Labs voice: ")
            useEL = True
            break
        elif user_input == 'no':
            break
        else:
            print("Invalid Input, please try again.")
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)
attention_dir = get_personality_dir(script_dir, attention_personality)

chatbot = kokoro.Kokoro(personality=personality_dir, 
                keys=keys, 
                voice_name=voicename
                )
attention_bot = kokoro.Kokoro(personality=attention_dir,
                              keys=keys,
                              voice_name=voicename)

assistant = streamer.Streamer(chatbot, attention_bot)

assistant.run(save_foldername=foldername_dir,
                useEL=useEL,
                usewhisper=usewhisper,
                timeout=1
                )
