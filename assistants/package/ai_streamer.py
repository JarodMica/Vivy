import threading
import time

from queue import Queue

from .kokoro import Kokoro
from .assistant_utils import *
from .youtube_api import YoutubeAPI

class AI_Streamer:
    def __init__(self, kokoro: Kokoro, 
                 youtube: YoutubeAPI,
                 save_foldername
                 ):
        
        self.kokoro = kokoro
        self.youtube = youtube
        self.save_foldername = save_foldername

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

        # Create an event to signal that the end command has been received
        self.end_received = threading.Event()

    def run(self):
        print("Starting up!")
        threads = []
        for func in [self.retrieve_comments, self.gpt_generation, self.separate_sentence, 
                     self.tts_generation, self.read_audio, self.handle_personal_input]:
            t = threading.Thread(target=func)
            t.start()
            threads.append(t)

        time.sleep(0.1)

    # Handle personal sentence input in a separate thread
    def handle_personal_input(self):
        while not self.end_received.is_set():
            personal_sentence = input("Enter your personal sentence (or 'this is the end' to stop): ")
            if personal_sentence.lower() == "this is the end":
                self.gpt_generation_queue.put(f"User said: {personal_sentence}")
                self.end_received.set()
            else:
                self.gpt_generation_queue.put(f"User said: {personal_sentence}")

    def retrieve_comments(self):
        while not self.end_received.is_set():
            if not self.youtube.msg_queue.empty():
                msg = self.youtube.msg_queue.get()
                print(f"{msg.datetime} [{msg.author.name}]- {msg.message}")
                complete_message = (f"{msg.author.name} said: {msg.message}")
                self.gpt_generation_queue.put(complete_message)
            
    def gpt_generation(self):
        while True:
            if not self.gpt_generation_queue.empty():
                comment = self.gpt_generation_queue.get()
                self.kokoro.messages.append({"role" : "user" , "content" : comment})
                response = self.kokoro.response_completion()
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
                tts_audio = self.kokoro.generate_voice(sentence)
                self.read_audio_queue.put(tts_audio)

    def read_audio(self):
        while True:
            if not self.read_audio_queue.empty():
                tts_audio = self.read_audio_queue.get()
                with self.audio_lock:
                    async_play_audio(tts_audio)
                self.audio_read.set()