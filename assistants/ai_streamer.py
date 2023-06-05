import os

from package import kokoro
from package import tortoise_api
from package import ai_streamer
from package import youtube_api
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "aistreamer"
personality = "aistreamer"
# attention_personality = "attention"
voicename = "Rem"
assistant_name = "Emi"
useEL = False
# usewhisper = False
useTortoise = True


script_dir = os.path.dirname(os.path.abspath(__file__))
    

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)

# attention_dir = get_personality_dir(script_dir, attention_personality)

# Instantiate classes
chatbot = kokoro.Kokoro(personality=personality_dir, 
                        keys=keys, 
                        voice_name=voicename
                        )

# Starts the comment collection thread
# video_id = input("Enter Video ID: ")
video_id = "MxpzI8e6Gxo"
youtube = youtube_api.YoutubeAPI(video_id, max_queue_length=2, collection_cycle_duration=2)
youtube.start()

if useTortoise:
    tortoise = tortoise_api.Tortoise_API()
else:
    print("No Tortoise installation")
    tortoise = None
    pass

assistant = ai_streamer.AI_Streamer(chatbot, 
                                    youtube, 
                                    foldername_dir, 
                                    tortoise)
assistant.run()
