import os
import sys
from package.gpt_assistant import ChatGPT

# The only variables that need to be modifed
foldername = "assistant"
personality = "assistant"
voicename = "Rem"

if getattr(sys, 'frozen', False):
    # running as a compiled executable
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
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
                   useEL=False
                   )
