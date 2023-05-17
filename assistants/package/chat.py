from .kokoro import Kokoro
from .assistant_utils import *

class Chat:
    def __init__(self, chatGPT: Kokoro):
        self.chatGPT = chatGPT

    def run(self, save_foldername, keyword ='hey', updatein='', useEL=False, usewhisper=False):
        '''
        Chat with an AI assistant using OpenAI's GPT-3 model.  Unlike the others, once you initiate
        the conversation with a keyword, it will just keep listening.  This means no timer on the amount
        of silence in between speaking, but it also means it's listening forever and will respond back
        until you quit out.  Check out assistant() or assistantp() if you want behavior closer to
        Google/Alexa.

        Args:
            save_foldername (str): The name of the folder to save the conversation history in.
            keyword (str) : The keyword to get the assistant listening
            updatein (str): The path of a file to read and update the "system" role for ChatGPT, does so by appending messages
            useEL (bool, optional): Whether to use Eleven Labs' API to generate and play audio. Defaults to False.
            usewhisper (bool, optional): Whether to use Whisper for voice recognition.  Defaults to False.
        '''
        while True:
            self.chatGPT.start_conversation(keyword=keyword)
            suffix = save_conversation(self.chatGPT.messages, save_foldername)
            while True:
                audio = self.chatGPT.listen_for_voice(timeout=None)
                try:
                    if usewhisper:
                        if audio:
                            user_input = self.chatGPT.whisper(audio)
                            print("You said: ", user_input) # Checking
                        else:
                            raise ValueError("Empty audio input")
                    else:    
                        user_input = self.chatGPT.r.recognize_google(audio)
                    
                except Exception as e:
                    print(e)
                    continue

                check_quit(user_input)
                
                # This merely appends the list of dictionaries, it doesn't overwrite the existing
                # entries.  It should change the behavior of chatGPT though based on the text file.
                if updatein != '':
                    if "update chat" in user_input.lower():
                            update = updatein
                            with open (update, "r") as file:
                                update = file.read()
                                self.chatGPT.messages.append({"role" : "system", "content" : update})

                self.chatGPT.messages.append({"role": "user", "content": user_input})

                try:
                    response = self.chatGPT.response_completion()
                    self.chatGPT.generate_voice(response=response, useEL=useEL)
                    save_inprogress(self.chatGPT.messages, suffix=suffix, save_foldername=save_foldername)
                except:
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.chatGPT.messages = [{"role": "system", "content": f"{self.chatGPT.mode}"}]
                    suffix = save_conversation(self.chatGPT.messages, save_foldername)
                