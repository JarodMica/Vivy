from gpt_assistant import ChatGPT

# Set-up personality, profession, or specialty of the bot
personality = "interview.txt"
system_change = "interview_end.txt"

# Set-up Eleven Labs voice
voicename = "Eren"

# name of folder to save conversations into
save_foldername = "interview"

# The magic bot:
chatbot = ChatGPT(personality, voicename)
chatbot.interview(save_foldername, system_change, useEL = False)

