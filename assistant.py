from gpt_assistant import ChatGPT

foldername = "assistant"
voicename = "Rem"
personality = "assistant.txt"

chatbot = ChatGPT(personality=personality, voice_name=voicename)
chatbot.assistant(save_foldername=foldername, useEL=True)
