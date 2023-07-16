import os

from package import kokoro
from package import ai_streamer
from package import youtube_api
from utils import get_file_paths

# The only variables that need to be modifed
foldername = "aistreamer"
personality = "aistreamer"
# attention_personality = "attention"
voicename = "Rem"
assistant_name = "Emi"
tts = "rvc"
video_id = "k_sNSdHB7cI"

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
        

    foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                        foldername, 
                                                        personality)

    # Instantiate classes
    _kokoro = kokoro.Kokoro(personality=personality_dir, 
                            keys=keys, 
                            save_folderpath=foldername_dir,
                            voice_name=voicename,
                            tts = tts,
                            tortoise_autoplay=False
                            )

    # Starts the comment collection thread
    youtube = youtube_api.YoutubeAPI(video_id, max_queue_length=2, collection_cycle_duration=10)
    youtube.start()
    assistant = ai_streamer.AI_Streamer(_kokoro, 
                                        youtube, 
                                        foldername_dir)
    assistant.run()
