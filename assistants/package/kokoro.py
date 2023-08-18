import speech_recognition as sr
import openai
import pyttsx3
import time
import yaml
import threading
import multiprocessing

from pydub.utils import mediainfo
from queue import Queue
from multiprocessing import Process

from .assistant_utils import *
from .tortoise_api import Tortoise_API
from elevenlabslib import *
from rvc_infer import rvc_convert

# Note to self, refactor code to use some type of list and index what TTS to use
def rvc_queue(q, done_q, rvc_model_path):
    while True:  # Could create zombie processes
        audio_path, opt_dir = q.get()
        rvc_convert(model_path=rvc_model_path,input_path=audio_path, output_dir_path=opt_dir)
        done_q.put(True)  # Signal that we're done processing this item

def worker(queue, done_event):
    while True:
        item = queue.get()
        try:
            final_audio = play_audio(item)
            queue.task_done()

            if final_audio == "FIN":
                done_event.set()
                break

        except Exception as e:
            print(f"Error in worker thread: {e}")


def get_audio_duration(file_path):
    """
    Get the duration of an audio file.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        float: Duration of the audio file in seconds.
    """
    audio_info = mediainfo(file_path)
    duration = float(audio_info['duration'])
    return duration

class Kokoro:
    def __init__(self, 
                personality:str, 
                keys:str,
                save_folderpath:str, 
                voice_name:str = "Rachel", 
                device_index = None, 
                gptmodel:str = "gpt-3.5-turbo",
                tts:str = "default",
                speech_recog:str = "google",
                keyword:str = 'hey',
                tortoise_autoplay:bool = True,
                rvc_model_path=None
                ):
        '''
        Initialize the ChatGPT class with all of the necessary arguments

        Args:
            personality (str) : path to the prompts or "personalities" .txt
            keys (str) : path to the keys.txt file
            save_folderpath(str) : path of folder to save conversations to
            voice_name (str) : Eleven Labs voice to use
            device_index (int) : microphone device to use (0 is default)
            gptmodel (str) : choose the openai GPT model to use
            tts (str) : choose which tts engine to use
            speech_recog (str) : determine what speech recognition to use (google or whisper)
            keyword(str) : keyword to start a conversation
            tortoise_autoplay (bool) : determine if tortoise autoplay's audio
        '''
        self.keyword = keyword
        self.speech_recog = speech_recog
        self.save_folderpath = save_folderpath
        self.suffix = get_suffix(save_folderpath)

        # Read in keys
        with open(keys, "r") as file:
            keys = yaml.safe_load(file)

        # GPT Set-Up
        self.OPENAI_KEY = keys['OPENAI_KEY']
        openai.api_key = self.OPENAI_KEY
        self.gptmodel = gptmodel

        # TTS area
        self.tts = tts
        try:
            if self.tts == "elevenlabs":
                self.EL_KEY = keys['EL_KEY']
                self.user = ElevenLabsUser(f"{self.EL_KEY}")
                try:
                    self.voice = self.user.get_voices_by_name(voice_name)[0]  # This is a list because multiple voices can have the same name
                except:
                    print("Setting default voice to Rachel")
                    print("(If you set a voice that you made, make sure it matches exactly)"
                            " as what's on the Eleven Labs page.  Capitilzation matters here.")
                    self.voice = self.user.get_voices_by_name("Rachel")[0] 
            elif self.tts == "tortoise" or "rvc":
                self.rvc_model_path = rvc_model_path
                self.tortoise = Tortoise_API()
                self.tortoise_autoplay = tortoise_autoplay
                # Queues for tortoise
                self.audio_queue = Queue()
                self.worker_thread = None
                self.done_event = threading.Event()
                self.proc = None
                self.q = multiprocessing.Queue()
                self.done_q = multiprocessing.Queue()
                self.suffix_counter = 1  # Initial suffix
            else:
                raise Exception("No valid TTS inputted into kokoro or SYSTEM chosen")
        except Exception as e:
            print(e)
            self.engine = pyttsx3.init()
            # self.engine.setProperty('rate', 180) #200 is the default speed, this makes it slower
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[1].id) # 0 for male, 1 for female

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
    def start_conversation(self):
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
                if f"{self.keyword}" in user_input:
                    print("Keyword heard")
                    break
                for i, word in enumerate(user_input):
                    check_quit(word)

    def response_completion(self, append=True):
        '''
        Notes:
            You can modify the parameters in the ChatCompletion to change how the bot responds
            using things like temperature, max_token, etc.  Reference the chatGPT API to 
            see what parameters are available to use.

        Args:
            append(bool) : determine whether to append response or not
        '''
        response = ""
        for api_attempts in range(3):
            try:
                completion = openai.ChatCompletion.create(
                    model=self.gptmodel,
                    messages=self.messages,
                    temperature=0.8
                )
                response = completion.choices[0].message.content
                break  # Break out of the loop if the code execution is successful
            except openai.APIError as e:
                if "maximum context" in str(e):
                    print("Token limit exceeded, clearing messages list and restarting")
                    self.messages = [{"role": "system", "content": f"{self.mode}"}]
                    self.suffix = get_suffix(self.save_folderpath)
                    continue
                elif "overloaded" in e.split():
                    print("OpenAI is overloaded at the moment")
                    continue
                else:
                    print("Something happened on OpenAI's end:", str(e))
                    time.sleep(10)  # Pause for 10 seconds before the next attempt
            except Exception as e:  # Catch other unexpected exceptions
                print("An unexpected error occurred:", str(e))
                self.messages = [{"role": "system", "content": f"{self.mode}"}]
                time.sleep(10)
        else:
            print("Failed after 3 attempts. Exiting the program.")
            
        if append:
            self.messages.append({"role": "assistant", "content": response})
        print(f"\n{response}\n")
        return response


    def generate_voice(self, sentence):
        '''
        Generate a TTS output based on the chosen engine.  Tortoise defaults to true for
        auto play, however, some assistants like AI streamer want the audio path instead
        to queue up audio to play.

        Available options: [tortoise, rvc, elevenlabs, system (default)]

        Args:
            sentence(str) : text to send over to tts engine

        Returns:
            audio_path(str) (tortoise ONLY) : path to audio file to play
        
        '''
        if self.tts == "tortoise":
            if self.tortoise_autoplay == True:
                # This is needed in order to cut down long sentences into more manageable chunks
                sentences = filter_paragraph(sentence)
                
                for sentence in sentences:
                    audio_path = self.tortoise.call_api(sentence)
                    # Start the worker thread if it's not already running
                    if self.worker_thread is None or not self.worker_thread.is_alive():
                        self.worker_thread = threading.Thread(target=worker, args=(self.audio_queue, self.done_event))
                        self.worker_thread.start()
                    # Add the audio file to the queue
                    self.audio_queue.put(audio_path)
                self.audio_queue.put("FIN")

                # Join the worker thread here
                self.worker_thread.join()
            else:
                audio_path = self.tortoise.call_api(sentence)
                return audio_path
            
        elif self.tts == "rvc":
            create_directory("output")
            opt = get_path("output")
            opt_dir = os.path.join(opt, f"rvc_out_{self.suffix_counter}.wav")
            self.suffix_counter = (self.suffix_counter % 5) + 1  # Increment the counter and wrap around after 5
            with open(opt_dir, 'a') as f:
                pass
            if self.tortoise_autoplay == True:
                # This is needed in order to cut down long sentences into more manageable chunks
                sentences = filter_paragraph(sentence)
                for sentence in sentences:
                    audio_path = self.tortoise.call_api(sentence)
                    rvc_convert(model_path=self.rvc_model_path, input_path=audio_path, output_dir_path=opt_dir)
                    
                    # Start the worker thread if it's not already running
                    if self.worker_thread is None or not self.worker_thread.is_alive():
                        self.worker_thread = threading.Thread(target=worker, args=(self.audio_queue,self.done_event))
                        self.worker_thread.start()
                        
                    # Add the audio file to the queue
                    self.audio_queue.put(opt_dir)
                self.audio_queue.put("FIN")
                # Join the worker thread here
                self.worker_thread.join()
            else:
                audio_path = self.tortoise.call_api(sentence)

                # Create a Process for rvc_convert
                if self.proc is None or not self.proc.is_alive():
                    self.proc = multiprocessing.Process(target=rvc_queue, args=(self.q, self.done_q, self.rvc_model_path))
                    self.proc.start()  # Starts the new process
                self.q.put((audio_path, opt_dir))
                
                # Wait for a signal in the done queue
                done_signal = self.done_q.get()
                if done_signal:
                    return opt_dir


        elif self.tts == "elevenlabs":
            self.voice.generate_and_play_audio(f"{sentence}", playInBackground=False)
        else: # default engine (windows voice)
            self.engine.say(f"{sentence}")
            self.engine.runAndWait()

        self.done_event.wait()
        
        print("Finished reading the audio paths.")

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
    
    def speech_recognition(self, audio):
        '''
        Decide which speech recognition software to use.  Choice between whisper (openAI API)
        and google (free)

        Args:
            audio(Audiodata) : user input from microphone
        '''
        try:
            if self.speech_recog == "whisper":
                user_input = self.whisper(audio)
                print("You said: ", user_input)
                return user_input
            else:
                raise Exception
        except:
            user_input = self.r.recognize_google(audio)

    def whisper(self, audio):
        '''
        Uses the Whisper API to generate text from user voice input. 

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
    
    def save_conversation(self):
        save_inprogress(self.messages, self.suffix, self.save_folderpath)


