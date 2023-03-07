from gpt_assistant import ChatGPT

# Set-up personality, profession, or specialty of the bot
personality = "roleplay.txt"

# Set-up Eleven Labs voice
voicename = "Rem"

# name of folder to save conversations into
save_foldername = "roleplay"

# The magic bot:
chatbot = ChatGPT(personality=personality, voice_name=voicename)
chatbot.chat(save_foldername=save_foldername, useEL = False)

