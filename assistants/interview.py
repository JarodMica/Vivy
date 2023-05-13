import sys 
import os

from package import kokoro
from package import interview
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "interview"
personality = "interview"
system_change = "interview_end"
voicename = "Rem"
useEL = False
usewhisper = True

# This code block only checks if it's being ran as a python script or as an exe
if getattr(sys, 'frozen', False):
    # script_dir = os.path.dirname(os.path.abspath(sys.executable))
    script_dir = sys._MEIPASS
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

foldername_dir, personality_dir, keys, syschange_dir = get_file_paths(script_dir, 
                                                                     foldername, 
                                                                     personality, 
                                                                     system_change)

chatbot = kokoro.Kokoro(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
assistant = interview.Interview(chatbot)

assistant.run(save_foldername=foldername_dir,
                  system_change=syschange_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )

