import threading
import time

from queue import Queue

from .kokoro import Kokoro
from .assistant_utils import *
from .tortoise_api import  Tortoise_API
from .tortoise_api import filter_paragraph
from .youtube_api import YoutubeAPI

class AI_Streamer:
    def __init__(self, chatGPT: Kokoro, 
                 youtube: YoutubeAPI,
                 save_foldername, 
                 tortoise: Tortoise_API | None = None,
                 useEL=False
                 ):
        
        self.chatGPT = chatGPT
        self.youtube = youtube
        self.save_foldername = save_foldername
        self.tortoise = tortoise
        self.useEL = useEL

        # Queues
        self.retrieve_comments_queue = Queue()
        self.gpt_generation_queue = Queue()
        self.separate_sentence_queue = Queue()
        self.tts_generation_queue = Queue()
        self.read_audio_queue = Queue()

        # Events
        self.gpt_generated = threading.Event()
        self.sentences_separated = threading.Event()
        self.tts_generated = threading.Event()
        self.audio_read = threading.Event()
        self.playing_audio = threading.Event()

        self.audio_lock = threading.Lock()

    def run(self):
        print("Starting up!")
        threads = []
        for func in [self.retrieve_comments, self.gpt_generation, self.separate_sentence, self.tts_generation, self.read_audio]:
            t = threading.Thread(target=func)
            t.start()
            threads.append(t)

        time.sleep(0.1)

    def retrieve_comments(self):
        while True:
            if not self.youtube.msg_queue.empty():
                msg = self.youtube.msg_queue.get()
                print(f"{msg.datetime} [{msg.author.name}]- {msg.message}")
                # Process the message through your chatGPT and tortoise, and send it to the TTS API
                complete_message = (f"{msg.author.name} said: {msg.message}")
                self.gpt_generation_queue.put(complete_message)
            
    def gpt_generation(self):
        while True:
            if not self.gpt_generation_queue.empty():
                comment = self.gpt_generation_queue.get()
                self.chatGPT.messages.append({"role" : "user" , "content" : comment})
                try:
                    response = self.chatGPT.response_completion()
                except:
                    print("Token limit exceeded, clearing messages list and restarting")
                    self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                self.separate_sentence_queue.put(response)


    def separate_sentence(self):
        while True:
            if not self.separate_sentence_queue.empty():
                gpt_response = self.separate_sentence_queue.get()
                sentences = filter_paragraph(gpt_response)
                for sentence in sentences:
                    self.tts_generation_queue.put(sentence)


    def tts_generation(self):
        while True:
            if not self.tts_generation_queue.empty():
                sentence = self.tts_generation_queue.get()
                tts_audio = self.tortoise.call_api(sentence, is_queue=False)
                self.read_audio_queue.put(tts_audio)


    def read_audio(self):
        while True:
            if not self.read_audio_queue.empty():
                tts_audio = self.read_audio_queue.get()
                with self.audio_lock:
                    play_audio(tts_audio)
                self.audio_read.set()

            
            
def play_audio(audio_path):
    data, sample_rate = sf.read(audio_path)
    channels = data.shape[1] if len(data.shape) > 1 else 1
    data = data.astype('float32')  # Convert the data to float32
    with sd.OutputStream(samplerate=sample_rate, channels=channels) as stream:
        stream.write(data)

    # os.remove(audio_path)