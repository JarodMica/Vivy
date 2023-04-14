import json
import speech_recognition as sr
from elevenlabslib import *
import os
import openai
import pyttsx3
import time
import winsound

class ChatGPT:
    def __init__(self, personality:str, keys:str, voice_name="Rachel", device_index=0):
        '''
        Initialize the ChatGPT class with all of the necessary arguments

        Args:
            personality (str)   : path to the prompts or "personalities" .txt
            keys (str)          : path to the keys.txt file
            voice_name (str)    : Eleven Labs voice to use
            device_index (int)  : microphone device to use (0 is default)
        '''
        # Read in keys
        with open(keys, "r") as file:
            keys = json.load(file)

        # pyttsx3 Set-up
        self.engine = pyttsx3.init()
        # self.engine.setProperty('rate', 180) #200 is the default speed, this makes it slower
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id) # 0 for male, 1 for female

        # GPT Set-Up
        self.GPT_KEY = keys['GPT_KEY']
        openai.api_key = self.GPT_KEY
        self.gptmodel = "gpt-3.5-turbo"

        # Eleven Labs Set-up
        try:
            self.EL_KEY = keys['EL_KEY'] #Eleven labs
            self.user = ElevenLabsUser(f"{self.EL_KEY}")
            try:
                self.voice = self.user.get_voices_by_name(voice_name)[0]  # This is a list because multiple voices can have the same name
            except:
                print("Setting default voice to Rachel")
                print("(If you set a voice that you made, make sure it matches exactly)"
                        " as what's on the Eleven Labs page.  Capitilzation matters here.")
                self.voice = self.user.get_voices_by_name("Rachel")[0] 
        except:
            print("No API Key set for Eleven Labs")

        # Mic Set-up
        self.r = sr.Recognizer()
        self.r.dynamic_energy_threshold=False
        self.r.energy_threshold = 300 # 300 is the default value of the SR library
        self.mic = sr.Microphone(device_index=device_index)

        # Set-up the system of chatGPT
        with open(personality, "r") as file:
            self.mode = file.read()

        self.messages  = [
            {"role": "system", "content": f"{self.mode}"}
        ]

# Different assistant modes starts here ---------------------------------------------------------------------------------------------------
    def chat(self, save_foldername, keyword ='hey', updatein='', useEL=False, usewhisper=False):
        '''
        Chat with an AI assistant using OpenAI's GPT-3 model.  Unlike the others, once you initiate
        the conversation with a keyword, it will just keep listening.  This means no timer on the amount
        of silence in between speaking, but it also means it's listening forever and will respond back
        until you quit out.  Check out assistant() or assistantp() if you want behavior closer to
        Google/Alexa.

        Args:
            save_foldername (str): The name of the folder to save the conversation history in.
            updatein (str): The path of a file to read and update the "system" role for ChatGPT, does so by appending messages
            useEL (bool, optional): Whether to use Eleven Labs' API to generate and play audio. Defaults to False.
        '''
        while True:
            self.start_conversation(keyword=keyword)
            suffix = self.save_conversation(save_foldername)
            while True:
                audio = self.listen_for_voice(timeout=None)
                try:
                    if usewhisper:
                        if audio:
                            user_input = self.whisper(audio)
                            print("You said: ", user_input) # Checking
                        else:
                            raise ValueError("Empty audio input")
                    else:    
                        user_input = self.r.recognize_google(audio)
                    
                except Exception as e:
                    print(e)
                    continue

                if "quit" in user_input.lower() or "quit." in user_input.lower():
                    raise SystemExit
                
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
                    self.save_inprogress(suffix=suffix, save_foldername=save_foldername)
                except:
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.messages = [{"role": "system", "content": f"{self.mode}"}]
                    suffix = self.save_conversation(save_foldername)
                
    
    def interview(self, save_foldername, system_change = '', useEL=False, usewhisper = False):
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

        suffix = self.save_conversation(save_foldername)
        start = ("Introduce yourself (pick a random name) and welcome the candidate in."
                "Let them know what they're applying for and then proceed by asking for an introduction."
                "Keep track but do not not inform the candidate about the points system")
        self.messages.append({"role": "user", "content": start})
        response = self.response_completion()
        self.generate_voice(response, useEL)
        while True:
            audio = self.listen_for_voice(timeout=None)
            try:
                if usewhisper == True:
                    user_input = self.whisper(audio)
                    print("You said: ", user_input) # Checking
                else:    
                    user_input = self.r.recognize_google(audio)
                
            except Exception as e:
                print(e)
                continue
            
            if "quit" in user_input.lower() or "quit." in user_input.lower():
                raise SystemExit
            
            self.messages.append({"role": "user", "content": user_input})
            try:
                response = self.response_completion()
                self.generate_voice(response, useEL)
                self.save_inprogress(suffix=suffix, save_foldername=save_foldername)

                if system_change != '':
                    # if the bot responds with this, changes "system" behavior
                    if "interview" and "is over" in response.lower():
                        system_change=system_change
                        with open(system_change, "r") as file:
                            system = file.read()

                        for message in self.messages:
                            if message['role'] == 'system':
                                message['content'] = system
            except Exception as e:
                print("Token limit exceeded, clearing messsages list and restarting")
                self.messages  = [{"role": "system", "content": f"{self.mode}"}]
                suffix = self.save_conversation(save_foldername)
                self.messages.append({"role": "user", "content": start})
                response = self.response_completion()
                self.generate_voice(response, useEL)

    def assistant(self, save_foldername, keyword ='hey', useEL = False, usewhisper = False, timeout = 5):
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
            # Beep to let you know it reset
            duration = 500  # milliseconds
            freq = 1000  # Hz
            winsound.Beep(freq, duration)

            self.start_conversation(keyword)
            self.messages = [{"role" : "system", "content" : f"{self.mode}"}]
            suffix = self.save_conversation(save_foldername)
            self.generate_voice("I'm listening.", useEL)
            start_time = time.time()
            while True:
                audio = self.listen_for_voice()
                try:
                    if usewhisper == True:
                        user_input = self.whisper(audio)
                        print("You said: ", user_input) # Checking
                    else:    
                        user_input = self.r.recognize_google(audio)
                    
                except :
                    if time.time() - start_time > timeout:
                        break
                    continue
                
                if "quit" in user_input.lower() or "quit." in user_input.lower():
                    raise SystemExit

                self.messages.append({"role" : "user", "content" : user_input})
                try:
                    response = self.response_completion()
                    self.generate_voice(response=response, useEL=useEL)
                    self.save_inprogress(suffix=suffix, save_foldername=save_foldername)
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.messages = [{"role": "system", "content": f"{self.mode}"}]
                    suffix = self.save_conversation(save_foldername)

    def assistantP(self, save_foldername, keyword ='hey', useEL = False, usewhisper = False, timeout = 5):
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
            # Beep to let you know it reset
            duration = 500  # milliseconds
            freq = 1000  # Hz
            winsound.Beep(freq, duration)

            self.start_conversation(keyword = keyword)
            self.generate_voice("I'm listening.", useEL)
            suffix = self.save_conversation(save_foldername)
            start_time = time.time()

            while True:
                audio = self.listen_for_voice()
                try:
                    if usewhisper == True:
                        user_input = self.whisper(audio)
                        print("You said: ", user_input) # Checking
                    else:    
                        user_input = self.r.recognize_google(audio)
                except :
                    if time.time() - start_time > timeout:
                        break
                    continue
                
                if "quit" in user_input.lower() or "quit." in user_input.lower():
                    raise SystemExit
                
                try:
                    self.messages.append({"role" : "user", "content" : user_input})
                    response = self.response_completion()
                    self.generate_voice(response=response, useEL=useEL)
                    self.save_inprogress(suffix=suffix, save_foldername=save_foldername)
                    start_time = time.time()
                except Exception as e:
                    print(f"{e}")
                    if "overloaded" in e.split():
                        continue
                    print("Token limit exceeded, clearing messsages list and restarting")
                    self.messages = [{"role": "system", "content": f"{self.mode}"}]
                    suffix = self.save_conversation(save_foldername)
 

 # Methods the assistants rely on------------------------------------------------------------------------------------------------------------------

    # This is to only initiate a conversation if you say "hey"
    def start_conversation(self, keyword = 'hey'):
        print("Initiated: ")
        while True:
            with self.mic as source:
                self.r.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.r.listen(source)
                try:
                    user_input = self.r.recognize_google(audio)
                    user_input = user_input.split()
                except:
                    continue
                # Key word in order to start the conversation 
                if f"{keyword}" in user_input:
                    print("true")
                    break
                if "quit" in user_input:
                    raise SystemExit
                else:
                    continue
    def save_conversation(self, save_foldername:str):
        '''
        Checks the folder for previous conversations and will get the next suffix that has not been used yet.

        Args:
            save_foldername (str) : Takes in the path to save the conversation to.
        Returns:
            suffix (int) : Needed to keep track of the conversation name for save_inprogress
        '''
        
        os.makedirs(save_foldername, exist_ok=True)
        base_filename = 'conversation'
        suffix = 0
        filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')

        while os.path.exists(filename):
            suffix += 1
            filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')
        with open(filename, 'w', encoding = 'utf-8') as file:
            json.dump(self.messages, file, indent=4, ensure_ascii=False)

        return suffix

    def save_inprogress(self, suffix, save_foldername):
        '''
        Uses the suffix number returned from save_conversation to continually update the 
        file for this instance of execution.  This is so that you can save the conversation 
        as you go so if it crashes, you don't lose to conversation.  Shouldn't be called
        from outside of the class.

        Args:
            suffix  :  Takes suffix count from save_conversation()
        '''

        os.makedirs(save_foldername, exist_ok=True)
        base_filename = 'conversation'
        filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')

        with open(filename, 'w', encoding = 'utf-8') as file:
            json.dump(self.messages, file, indent=4, ensure_ascii=False)

    def response_completion(self):
        '''
        Notes:
            You can modify the parameters in the ChatComplete to change how the bot responds
            using things like temperature, max_token, etc.  Reference the chatGPT API to 
            see what parameters are available to use.
        '''
        completion = openai.ChatCompletion.create(
                model=self.gptmodel,
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

    def listen_for_voice(self, timeout:int|None=5):
        with self.mic as source:
            print("\n Listening...")
            self.r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.r.listen(source, timeout)
            except:
                return []
        print("no longer listening")
        return audio
    
    def whisper(self, audio):
        '''
        Uses the Whisper API to generate audio for the response text. 

        Args:
            audio (AudioData) : AudioData instance used in Speech Recognition, needs to be written to a
                                file before uploading to openAI.
        Returns:
            response (str): text transcription of what Whisper deciphered
        '''
        self.r.recognize_google(audio) # raise exception for bad/silent audio
        with open('speech.wav','wb') as f:
            f.write(audio.get_wav_data())
        speech = open('speech.wav', 'rb')
        model_id = "whisper-1"
        completion = openai.Audio.transcribe(
            model=model_id,
            file=speech
        )
        response = completion['text']
        return response
