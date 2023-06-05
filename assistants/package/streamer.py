import time

from .kokoro import Kokoro
from .assistant_utils import *
from .tortoise_api import  Tortoise_API
from .tortoise_api import filter_paragraph

class Streamer:
    '''
    This takes in two instantiations of Kokoro, so make sure to set them
    both up in the assistant script
    '''
    def __init__(self, chatGPT: Kokoro, attention: Kokoro, tortoise: Tortoise_API | None = None):
        self.chatGPT = chatGPT
        self.attention = attention
        self.tortoise = tortoise

    def run(self, save_foldername, useEL=False, usewhisper=False, timeout = 1, assistant_name: str = "Vivy"):
        # Create two agents: 
        # one to generate conversation generate_response()
        # one to filter user input attention()
        # after attention responds yes, proceed with responding
        # via generate_response()
        # give the user 5 seconds to continue talking, then
        # go back to a listening state and repeat
        while True:
            suffix = save_conversation(self.chatGPT.messages, save_foldername)
            while True:
                audio = self.chatGPT.listen_for_voice()
                try:
                    if usewhisper:
                        user_input = self.chatGPT.whisper(audio)
                        print("You said: ", user_input) # Checking    
                    else:
                        user_input = self.chatGPT.r.recognize_google(audio)
                
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
                    self.chatGPT.messages.append({"role" : "user", "content" : user_input})
                    self.streamer_completion(save_foldername, suffix, useEL)

                start_time = time.time()
                while True:
                    audio = self.chatGPT.listen_for_voice()
                    try:
                        if usewhisper:
                            user_input = self.chatGPT.whisper(audio)
                            print("You said: ", user_input) # Checking    
                        else:
                            user_input = self.chatGPT.r.recognize_google(audio)
                    except Exception as e:
                        if time.time() - start_time > timeout:
                            break
                        continue
                    
                    try:
                        self.chatGPT.messages.append({"role" : "user" , "content" : user_input})
                        self.streamer_completion(save_foldername, suffix, useEL)
                        start_time = time.time()
                    except Exception as e:
                        print(f"{e}")
                        if "overloaded" in e.split():
                            continue
                        print("Token limit exceeded, clearing messsages list and restarting")
                        self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                        suffix = save_conversation(self.chatGPT.messages, save_foldername)


    def streamer_completion(self, save_foldername, suffix, useEL):
        try:
            response = self.chatGPT.response_completion()
            if self.tortoise:
                sentences = filter_paragraph(response)
                self.tortoise.run(sentences) #sentence tortoise
            else:
                self.chatGPT.generate_voice(response, useEL)

            save_inprogress(self.chatGPT.messages, suffix, save_foldername)
        except:
            print("Token limit exceeded, clearing messsages list and restarting")
            self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
            suffix = save_conversation(self.chatGPT.messages, save_foldername)

                
