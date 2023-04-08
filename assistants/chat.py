import os
import sys
from package.gpt_assistant import ChatGPT
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

chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )

chatbot.chat(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )
