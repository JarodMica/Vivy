import os
import sys
from package.gpt_assistant import ChatGPT


# The only variables that need to be modifed
foldername = "interview"
personality = "interview"
system_change = "interview_end"
voicename = "Rem"
useEL = False

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
syschange_dir = os.path.join(script_dir,f"prompts/{system_change}.txt")
keys = os.path.join(script_dir,"keys.txt")


chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
chatbot.interview(save_foldername=foldername_dir,
                  system_change=syschange_dir,
                   useEL=useEL
                   )

