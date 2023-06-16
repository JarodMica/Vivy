from .kokoro import Kokoro
from .assistant_utils import *

class Chat:
    def __init__(self, kokoro: Kokoro):
        self.kokoro = kokoro

    def run(self):
        '''
        Chat with an AI assistant using OpenAI's GPT-3 model.  Unlike the others, once you initiate
        the conversation with a keyword, it will just keep listening.  This means no timer on the amount
        of silence in between speaking, but it also means it's listening forever and will respond back
        until you quit out.  Check out assistant() or assistantp() if you want behavior closer to
        Google/Alexa.

        '''

        while True:
            self.kokoro.start_conversation()
            while True:
                audio = self.kokoro.listen_for_voice(timeout=None)
                try:
                    user_input = self.kokoro.speech_recognition(audio)
                except Exception as e:
                    print(e)
                    continue

                check_quit(user_input)
        
                self.kokoro.messages.append({"role": "user", "content": user_input})
                response = self.kokoro.response_completion()
                self.kokoro.generate_voice(response)
                self.kokoro.save_conversation()
            
                