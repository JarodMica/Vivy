import time

from .kokoro import Kokoro
from .assistant_utils import *

class Assistant:
    def __init__(self, kokoro: Kokoro):
        self.kokoro = kokoro

    def run(self, timeout = 5):
        '''
        This method acts as more of a "tradtional" smart assistant such as google or alexa and is FORGETFUL, meaning it  
        will start over the current conversation once it times out. This means it's best used for 1 question 
        and some quick follow-up questions.  It waits for some keyword (if not specified, it will be "hey") and
        then proceeeds to the "conversation". Once in the conversation, you will be able to interact with the assistant 
        as you would normally, butif no speech is detected after 5 seconds (adjustable), the conversation will reset and 
        the assistant will need to be re-initiated with "hey".  

        Args:
            timeout : the amount of time the assistant will wait before resetting
        '''

        while True:
            self.kokoro.messages  = [{"role": "system", "content": f"{self.kokoro.mode}"}]
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
                
                if "quit" in user_input.lower() or "quit." in user_input.lower():
                    raise SystemExit

                self.kokoro.messages.append({"role" : "user", "content" : user_input})
                try:
                    response = self.kokoro.response_completion()
                    self.kokoro.generate_voice(response)
                    self.kokoro.save_conversation()
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
