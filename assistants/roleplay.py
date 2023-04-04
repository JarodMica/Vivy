from package.gpt_assistant import ChatGPT
from utils import get_user_input, get_file_paths

# The only variables that need to be modifed
foldername = "roleplay"
personality = "roleplay"
voicename = "Rem"
useEL = False
usewhisper = True

script_dir = get_user_input()

foldername_dir, personality_dir, keys = get_file_paths(script_dir, foldername, personality)


chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
chatbot.chat(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )
