import speech_recognition as sr
import openai
import pyttsx3
import yaml
from .assistant_utils import *

from elevenlabslib import *


class Kokoro:
    def __init__(self, personality:str, keys:str, voice_name="Rachel", device_index=None, gptmodel:str="gpt-3.5-turbo"):
        '''
        Initialize the ChatGPT class with all of the necessary arguments

        Args:
            personality (str)   : path to the prompts or "personalities" .txt
            keys (str)          : path to the keys.txt file
            voice_name (str)    : Eleven Labs voice to use
            device_index (int)  : microphone device to use (0 is default)
            gptmodel (str)      : choose the openai GPT model to use
        '''
        # Read in keys
        with open(keys, "r") as file:
            keys = yaml.safe_load(file)

        # pyttsx3 Set-up
        self.engine = pyttsx3.init()
        # self.engine.setProperty('rate', 180) #200 is the default speed, this makes it slower
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id) # 0 for male, 1 for female

        # GPT Set-Up
        self.OPENAI_KEY = keys['OPENAI_KEY']
        openai.api_key = self.OPENAI_KEY
        self.gptmodel = gptmodel

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
        self.r.energy_threshold = 150 # 300 is the default value of the SR library
        self.mic = sr.Microphone(device_index=device_index)

        # Set-up the system of chatGPT
        with open(personality, "r", encoding="utf-8") as file:
            self.mode = file.read()

        self.messages  = [
            {"role": "system", "content": f"{self.mode}"}
        ]

 # Methods the assistants rely on------------------------------------------------------------------------------------------------------------------

    # This is to only initiate a conversation if you say "hey"
    def start_conversation(self, keyword = 'hey'):
        while True:
            with self.mic as source:
                print("Adjusting to envionrment sound...\n")
                self.r.adjust_for_ambient_noise(source, duration=1.0)
                print("Listening: ")
                audio = self.r.listen(source)
                print("Done listening.")
                try:
                    user_input = self.r.recognize_google(audio)
                    print(f"Google heard: {user_input}\n")
                    user_input = user_input.split()
                except:
                    print(f"Google couldn't process the audio\n")
                    continue
                # Key word in order to start the conversation 
                if f"{keyword}" in user_input:
                    print("Keyword heard")
                    break
                for i, word in enumerate(user_input):
                    check_quit(word)

    def response_completion(self, append=True):
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
        if append:
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
