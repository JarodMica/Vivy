import time

from .kokoro import Kokoro
from .assistant_utils import *

class Assistant:
    def __init__(self, chatGPT: Kokoro):
        self.chatGPT = chatGPT

    def run(self, save_foldername, keyword ='hey', useEL = False, usewhisper = False, timeout = 5):
        '''
        This method acts as more of a "tradtional" smart assistant such as google or alexa and is FORGETFUL, meaning it  
        will start over the current conversation once it times out. This means it's best used for 1 question 
        and some quick follow-up questions.  It waits for some keyword (if not specified, it will be "hey") and
        then proceeeds to the "conversation". Once in the conversation, you will be able to interact with the assistant 
        as you would normally, butif no speech is detected after 5 seconds (adjustable), the conversation will reset and 
        the assistant will need to be re-initiated with "hey".  

        Args:
            save_foldername (str): The name of the folder where the conversation will be saved.
            keyword (str): The keyword(s) that will initiate the conversation
            useEL (bool, optional): If false, the bot generates responses using the system voices
            usewhipser (bool, optional): Defaults to False to use google speech recognition
            timeout : the amount of time the assistant will wait before resetting
        '''

        while True:
            beep()
            self.chatGPT.start_conversation(keyword)
            self.chatGPT.messages = [{"role" : "system", "content" : f"{self.chatGPT.mode}"}]
            suffix = save_conversation(self.chatGPT.messages, save_foldername)
            self.chatGPT.generate_voice("I'm listening.", useEL)
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
                
                if "quit" in user_input.lower() or "quit." in user_input.lower():
                    raise SystemExit

                self.chatGPT.messages.append({"role" : "user", "content" : user_input})
                try:
                    response = self.chatGPT.response_completion()
                    self.chatGPT.generate_voice(response=response, useEL=useEL)
                    save_inprogress(self.chatGPT.messages, suffix=suffix, save_foldername=save_foldername)
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                    suffix = save_conversation(self.chatGPT.messages, save_foldername)
