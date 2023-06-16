from .kokoro import Kokoro
from .assistant_utils import *

class Interview:
    def __init__(self, kokoro: Kokoro):
        self.kokoro = kokoro

    def run(self):
        '''
        Nearly identical to how the chat method works but this method conducts an interview 
        with a candidate using an interview bot style.  The actual only difference here is the
        assistant starts out in this case. 
        '''
        response = self.kokoro.response_completion()
        self.kokoro.generate_voice(response)
        while True:
            audio = self.kokoro.listen_for_voice(timeout=None)
            try:
                user_input = self.kokoro.speech_recognition(audio)
            except Exception as e:
                print(e)
                continue
            
            if "quit" in user_input.lower() or "quit." in user_input.lower():
                raise SystemExit
            
            self.kokoro.messages.append({"role": "user", "content": user_input})
            response = self.kokoro.response_completion()
            self.kokoro.generate_voice(response)
            self.kokoro.save_conversation()