import os
from gpt_assistant import ChatGPT

# Set-up personality, profession, or specialty of the bot
current_directory = os.getcwd()
personality = "roleplay.txt"
directory = os.path.join(current_directory,'prompts', personality)

# Set-up Eleven Labs voice
voicename = "Rem"

# name of folder to save conversations into
save_foldername = "rem"

# The magic bot:
chatbot = ChatGPT(directory, voicename)
chatbot.interview(save_foldername, useEL = False)

