import os
import sys
from package.gpt_assistant import ChatGPT

# The only variables that need to be modifed
foldername = "one-up"
personality = "one-up"
voicename = "Rem"
useEL = False
usewhisper = True

if getattr(sys, 'frozen', False):
    # running as a compiled executable
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
    # running as a script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

foldername_dir = os.path.join(script_dir,f"conversations/{foldername}")
personality_dir = os.path.join(script_dir,f"prompts/{personality}.txt")
keys = os.path.join(script_dir,"keys.txt")


chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
chatbot.assistant(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )
