import sys 
import os

from package import kokoro
from package import chat
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "chat"
personality = "chat"
voicename = "Rem"
useEL = False
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

chatbot = kokoro.Kokoro(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )

assistant = chat.Chat(chatbot)

assistant.run(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )
