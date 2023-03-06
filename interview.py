import os
from gpt_assistant import ChatGPT

# Set-up personality, profession, or specialty of the bot
current_directory = os.getcwd()
personality = "interview.txt"
directory = os.path.join(current_directory,'prompts', personality)
system_change = "interview_end.txt"
change_directory = os.path.join(current_directory,'prompt', system_change)

# Set-up Eleven Labs voice
voicename = "Eren"

# name of folder to save conversations into
save_foldername = "interview"

# The magic bot:
chatbot = ChatGPT(directory, voicename)
chatbot.interview(save_foldername, change_directory, useEL = False)

