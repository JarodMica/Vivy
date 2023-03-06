import json
import key
import speech_recognition as sr
from elevenlabslib import *
import os
import openai
import pyttsx3


class ChatGPT:
    def __init__(self, personality, voice_name="Vivy"):
        # pyttsx3 Set-up
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices') 
        self.engine.setProperty('voice', self.voices[1].id) # 0 for male, 1 for female

        # GPT Set-Up
        self.GPT_KEY = key.GPT_KEY 
        openai.api_key = self.GPT_KEY

        # Eleven Labs Set-up
        self.EL_KEY = key.EL_KEY #Eleven labs
        self.user = ElevenLabsUser(f"{self.EL_KEY}")
        self.voice = self.user.get_voices_by_name(voice_name)[0]  # This is a list because multiple voices can have the same name

        # Mic Set-up
        self.r = sr.Recognizer()
        self.r.dynamic_energy_threshold=False
        self.r.energy_threshold = 400
        self.mic = sr.Microphone(device_index=1)

        # Set-up the system of chatGPT
        self.mode = personality
        with open(f"{self.mode}", "r") as file:
            self.mode = file.read()

        self.messages  = [
            {"role": "system", "content": f"{self.mode}"}
        ]

    # This is to only initiate a conversation if you say "hey"
    def start_conversation(self):

        print("Initiated: ")
        while True:
            with self.mic as source:
                self.r.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.r.listen(source)
                try:
                    user_input = self.r.recognize_google(audio)
                    user_input = user_input.split()
                except:
                    continue
                # Key word in order to start the conversation
                if "hey" in user_input:
                    print("true")
                    break
                else:
                    continue

    
    def chat(self, save_foldername, updatein='', useEL=False):
        '''Chat with an AI assistant using OpenAI's GPT-3 model.
        Args:
            save_foldername (str): The name of the folder to save the conversation history in.
            updatein (str): The path of a file to read and update the "system" role for ChatGPT
            useEL (bool, optional): Whether to use Eleven Labs' API to generate and play audio. Defaults to False.
        Notes:
            - This method handles all of the chatting.
            - During the conversation, the user's speech is transcribed, and the response is generated using OpenAI's GPT-3 model.
            - The conversation history is saved to a file in the specified folder.
            - If the `update chat` command is spoken, the "system" role will be updated useing the path passed in from updatein
        '''
        self.start_conversation()
        suffix = self.save_conversation(save_foldername)
        while True:
            audio = self.listen_for_voice()
            try:
                user_input = self.r.recognize_google(audio)
            except:
                continue

            if "quit" in user_input.split():
                break
            
            # This merely appends the list of dictionaries, it doesn't overwrite the existing
            # entries.  It should change the behavior of chatGPT though based on the text file.
            if updatein != '':
                if "update chat" in user_input.lower():
                        update = updatein
                        with open (update, "r") as file:
                            update = file.read()
                            self.messages.append({"role" : "system", "content" : update})

            self.messages.append({"role": "user", "content": user_input})

            try:
                response = self.response_completion()
                self.generate_voice(response=response, useEL=useEL)
                self.save_inprogress(suffix=suffix, folder_name=save_foldername)
            except:
                print("Token limit exceeded, clearing messsages list and restarting")
                self.messages = []
                suffix = self.save_conversation(save_foldername)
                
    
    def interview(self, save_foldername, system_change, useEL=False):
        '''
        Nearly identical to how the chat method works but this method conducts an interview 
        with a candidate using an interview bot style. The conversation is saved to a 
        specified folder and "system_change" is used to modify how the system operates (I use it to end the 
        interview, but you can use any text format you would like)

        Args:
            save_foldername (str): The name of the folder where the conversation will be saved.
            system_change (str): A file name that contains the modified system behavior.
            useEL (bool, optional): If false, the bot generates responses using the system voices
        '''

        suffix = self.save_conversation(save_foldername)
        start = ("Introduce yourself (pick a random name) and welcome the candidate in."
                "Let them know what they're applying for and then proceed by asking for an introduction."
                "Keep track but do not not inform the candidate about the points system")
        self.messages.append({"role": "user", "content": start})
        response = self.response_completion()
        self.generate_voice(response, useEL)
        while True:
            audio = self.listen_for_voice()
            try:
                user_input = self.r.recognize_google(audio)
            except:
                continue

            if "quit" in user_input.split():
                break

            self.messages.append({"role": "user", "content": user_input})
            try:
                response = self.response_completion()
                self.generate_voice(response, useEL)
                self.save_inprogress(suffix=suffix, folder_name=save_foldername)
                 # if the bot responds with this, changes "system" behavior
                if "interview" and "is over" in response.lower():
                    system_change = system_change
                    with open(f"{system_change}", "r") as file:
                        system = file.read()

                    for message in self.messages:
                        if message['role'] == 'system':
                            message['content'] = system
            except:
                print("Token limit exceeded, clearing messsages list and restarting")
                self.messages  = [
                    {"role": "system", "content": f"{self.mode}"}
                ]
                suffix = self.save_conversation(save_foldername)
                self.messages.append({"role": "user", "content": start})
                response = self.response_completion()
                self.generate_voice(response, useEL)
 
    '''
    There are two methods that save files, one save_conversation and the other save_inprogress
    save_conversation : checks the folder for previous conversations and will get the next suffix
                        that has not been used yet.  It returns suffix number
    save_inprogress   : Uses the suffix number returned from save_conversation to continually update
                        the file for this instance of execution.  This is so that you can save the 
                        conversation as you go so if it crashes, you don't lose to conversation.

    Args:
        folder_name (str): Name of the folder to save to in the directory
    '''
    def save_conversation(self, folder_name="standard"):
        current_directory = os.getcwd()
        directory = os.path.join(current_directory, 'conversations', folder_name)
        os.makedirs(directory, exist_ok=True)

        base_filename = 'conversation'
        suffix = 0
        filename = os.path.join(directory, f'{base_filename}_{suffix}.txt')

        while os.path.exists(filename):
            suffix += 1
            filename = os.path.join(directory, f'{base_filename}_{suffix}.txt')

        with open(filename, 'w') as file:
            json.dump(self.messages, file, indent=4)

        return suffix

    def save_inprogress(self, suffix, folder_name="standard"):
        current_directory = os.getcwd()
        directory = os.path.join(current_directory, 'conversations', folder_name)
        os.makedirs(directory, exist_ok=True)

        base_filename = 'conversation'
        filename = os.path.join(directory, f'{base_filename}_{suffix}.txt')

        with open(filename, 'w') as file:
            json.dump(self.messages, file, indent=4)

    def response_completion(self):
        '''
        Notes:
            - You can modify the parameters in the ChatComplete to change how the bot responds
                using things like temperature, max_token, etc.  Reference the chatGPT API to 
                see what parameters are available to use.
        '''
        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages=self.messages,
                temperature=0.8
            )
        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        print(f"\n{response}\n")
        return response
    
    def generate_voice(self, response, useEL):
        if useEL == True:
                self.voice.generate_and_play_audio(f"{response}", playInBackground=False)
        else:
            self.engine.say(f"{response}")
            self.engine.runAndWait()

    def listen_for_voice(self):
        with self.mic as source:
                print("\n Listening...")
                self.r.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.r.listen(source)
        print("no longer listening")
        return audio