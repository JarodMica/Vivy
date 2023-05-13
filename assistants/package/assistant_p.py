import time

from .kokoro import Kokoro
from .assistant_utils import *

class AssistantP:
    def __init__(self, chatGPT: Kokoro):
        self.chatGPT = chatGPT

    def run(self, save_foldername, keyword ='hey', useEL = False, usewhisper = False, timeout = 5):
        '''
        Nearly identical to assistant, but maintains a persistent (p) memory of the conversation.  This means
        when it timesout after 5 seconds, it will maintain memory of the current conversation up until you restart
        or the token limit is reached. 

        Args:
            save_foldername (str): The name of the folder where the conversation will be saved.
            keyword (str): The keyword(s) that will initiate the conversation
            useEL (bool, optional): If false, the bot generates responses using the system voices
            usewhipser (bool, optional): If false, uses google speech recognition
            timeout : the amount of time the assistant will wait before resetting
        '''

        while True:
            beep()
            self.chatGPT.start_conversation(keyword = keyword)
            self.chatGPT.generate_voice("I'm listening.", useEL)
            suffix = save_conversation(self.chatGPT.messages, save_foldername)
            start_time = time.time()

            while True:
                audio = self.chatGPT.listen_for_voice()
                try:
                    if usewhisper == True:
                        user_input = self.chatGPT.whisper(audio)
                        print("You said: ", user_input) # Checking
                    else:    
                        user_input = self.chatGPT.r.recognize_google(audio)
                except :
                    if time.time() - start_time > timeout:
                        break
                    continue
                
                check_quit(user_input)
                
                try:
                    self.chatGPT.messages.append({"role" : "user", "content" : user_input})
                    response = self.chatGPT.response_completion()
                    self.chatGPT.generate_voice(response=response, useEL=useEL)
                    save_inprogress(self.chatGPT.messages, suffix=suffix, save_foldername=save_foldername)
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
                    if "overloaded" in e.split():
                        continue
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                    suffix = save_conversation(self.chatGPT.messages, save_foldername)