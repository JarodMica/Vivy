from package.gpt_assistant import ChatGPT
from utils import get_user_input, get_file_paths


# The only variables that need to be modifed
foldername = "interview"
personality = "interview"
system_change = "interview_end"
voicename = "Rem"
useEL = False
usewhisper = True


script_dir = get_user_input()

foldername_dir, personality_dir, keys, syschange_dir= get_file_paths(script_dir, 
                                                                     foldername, 
                                                                     personality, 
                                                                     system_change)

chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
chatbot.interview(save_foldername=foldername_dir,
                  system_change=syschange_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )

