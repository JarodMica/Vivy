import time

from .kokoro import Kokoro
from .assistant_utils import *
from .tortoise_api import filter_paragraph

class Streamer:
    '''
    This takes in two instantiations of Kokoro, so make sure to set them
    both up in the assistant script
    '''
    def __init__(self, kokoro: Kokoro, attention: Kokoro):
        self.kokoro = kokoro
        self.attention = attention

    def run(self, timeout = 1, assistant_name: str = "Vivy"):
        while True:
            audio = self.kokoro.listen_for_voice()
            try:
                user_input = self.kokoro.speech_recognition(audio)
            except Exception as e:
                print(e)
                continue

            check_quit(user_input)

            modified_text = self.attention.mode.replace('<<user_input>>', user_input)
            modified_text = modified_text.replace('<<name>>', assistant_name)

            self.attention.messages = [{"role" : "user", "content" : modified_text}]
            check_attention = self.attention.response_completion()
            
            if "no" in check_attention.lower():
                continue
            else:
                self.kokoro.messages.append({"role" : "user", "content" : user_input})
                response = self.kokoro.response_completion()
                if self.kokoro.tts == "tortoise":
                    sentences = filter_paragraph(response)
                    self.kokoro.tortoise.run(sentences)
                else:
                    self.kokoro.generate_voice(response)

            self.kokoro.save_conversation()
            
            start_time = time.time()
            while True:
                audio = self.kokoro.listen_for_voice()
                try:
                    self.kokoro.speech_recognition(audio)
                except Exception as e:
                    if time.time() - start_time > timeout:
                        break
                    continue
                
                self.kokoro.messages.append({"role" : "user" , "content" : user_input})
                response = self.kokoro.response_completion()
                if self.kokoro.tts == "tortoise":
                    sentences = filter_paragraph(response)
                    self.kokoro.tortoise.run(sentences)
                else:
                    self.kokoro.generate_voice(response)

                start_time = time.time()

                
