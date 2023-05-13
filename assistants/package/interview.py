from .kokoro import Kokoro
from .assistant_utils import *

class Interview:
    def __init__(self, chatGPT: Kokoro):
        self.chatGPT = chatGPT

    def run(self, save_foldername, system_change = '', useEL=False, usewhisper = False):
        '''
        Nearly identical to how the chat method works but this method conducts an interview 
        with a candidate using an interview bot style. The conversation is saved to a 
        specified folder and "system_change" is used to modify how the system operates (I use it to end the 
        interview, but you can use any text format you would like)

        Args:
            save_foldername (str): The name of the folder where the conversation will be saved.
            system_change (str): path to the personality change .txt file
            useEL (bool, optional): If false, the bot generates responses using the system voices
            usewhipser (bool, optional); If false, uses google speech recognition
        '''

        suffix = save_conversation(self.chatGPT.messages, save_foldername)
        start = ("Introduce yourself (pick a random name) and welcome the candidate in."
                "Let them know what they're applying for and then proceed by asking for an introduction."
                "Keep track but do not not inform the candidate about the points system")
        self.chatGPT.messages.append({"role": "user", "content": start})
        response = self.chatGPT.response_completion()
        self.chatGPT.generate_voice(response, useEL)
        while True:
            audio = self.chatGPT.listen_for_voice(timeout=None)
            try:
                if usewhisper == True:
                    user_input = self.chatGPT.whisper(audio)
                    print("You said: ", user_input) # Checking
                else:  
                    user_input = self.chatGPT.r.recognize_google(audio)
                
            except Exception as e:
                print(e)
                continue
            
            if "quit" in user_input.lower() or "quit." in user_input.lower():
                raise SystemExit
            
            self.chatGPT.messages.append({"role": "user", "content": user_input})
            try:
                response = self.chatGPT.response_completion()
                self.chatGPT.generate_voice(response, useEL)
                save_inprogress(self.chatGPT.messages, suffix=suffix, save_foldername=save_foldername)

                if system_change != '':
                    # if the bot responds with this, changes "system" behavior
                    if "interview" and "is over" in response.lower():
                        system_change=system_change
                        with open(system_change, "r", encoding="utf-") as file:
                            system = file.read()

                        for message in self.chatGPT.messages:
                            if message['role'] == 'system':
                                message['content'] = system
            except Exception as e:
                print("Token limit exceeded, clearing messsages list and restarting")
                self.chatGPT.messages  = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                suffix = save_conversation(self.chatGPT.messages, save_foldername)
                self.chatGPT.messages.append({"role": "user", "content": start})
                response = self.chatGPT.response_completion()
                self.chatGPT.generate_voice(response, useEL)