from package.gpt_assistant import ChatGPT
from utils import get_user_input, get_file_paths

# The only variables that need to be modifed
foldername = "assistant"
personality = "assistant"
voicename = "Rem"
useEL = False
usewhisper = True

script_dir = get_user_input()

foldername_dir, personality_dir, keys = get_file_paths(script_dir, foldername, personality)

# Initialize the chat assitant with the variables that you've set 
chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )

chatbot.assistant(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )
