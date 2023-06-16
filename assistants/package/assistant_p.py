import time

from .kokoro import Kokoro
from .assistant_utils import *

class AssistantP:
    def __init__(self, kokoro: Kokoro):
        self.kokoro = kokoro

    def run(self, timeout = 5):
        '''
        Nearly identical to assistant, but maintains a persistent (p) memory of the conversation.  This means
        when it timesout after 5 seconds, it will maintain memory of the current conversation up until you restart
        or the token limit is reached. 

        Args:
            timeout : the amount of time the assistant will wait before resetting
        '''
        
        while True:
            beep()
            self.kokoro.start_conversation()
            self.kokoro.generate_voice("I'm listening.")
            
            start_time = time.time()

            while True:
                audio = self.kokoro.listen_for_voice()
                try:
                    user_input = self.kokoro.speech_recognition(audio)
                except :
                    if time.time() - start_time > timeout:
                        break
                    continue
                
                check_quit(user_input)
                
                try:
                    self.kokoro.messages.append({"role" : "user", "content" : user_input})
                    response = self.kokoro.response_completion()
                    self.kokoro.generate_voice(response)
                    self.kokoro.save_conversation()
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
                    