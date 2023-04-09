# QUICK DESCRIPTION:

This repo utilizes OpenAI's GPT-3.5 Turbo model to engage in personalized conversations with users, catering to their preferred communication style. As GPT-3.5 Turbo serves as the foundation for ChatGPT, this project essentially shares its underlying model. Ultimately, the aim of this project is to develop a personal assistant that emulates human-like interactions. As the project is a work in progress, its features will expand as I continue to refine and iterate on the concept.

The fastest way to try these assistants would be to setup your API keys in the ```key.txt``` file and then run the exe files I have provided.  For this to work, **you must** rename ```keys_example.txt``` to be ```keys.txt```.  To find the exe files, check the latest release for this project https://github.com/JarodMica/Vivy/releases/

## YouTube Tutorial 
https://youtu.be/0qpar5R1VA4

## EXE Quick Use

If you just want to try out the assistants, download the zip folder and then unzip it to any location on your PC. Once unzipped, rename the keys txt file to ```keys.txt``` and then set up your API Keys in ```key.txt```. Now you can do two things, run the exe and try it out or adjust the prompts in the prompts folder.  If you run interview.exe, it's going to use the interview.txt file (same with roleplay). Else, you can modify the prompts to your own case and then run the exe files.

## How the chat assistant currrently works (there are others):
In general, this is how it work:
1. Run python script and it will start with "Initializing".  Now it's in a "listening" state.
2. The AI assistant is activated when the user says "hey" or anything containing this keyword ("they" does not work)
3. Now the user can speak to the AI, it'll listen until you stop speaking (default is 0.8 seconds)
4. It then transcribes the user's speech and generates a response using ChatGPT
5. It will read out the response.
6. The conversation history is saved to a file in a specified folder and the program loops.

If you say quit, it will quit.

#### The following libraries are required to run the ChatGPT class:
- ```SpeechRecognition```
- ```elevenlabslib```
- ```openai```
- ```pyttsx3```
- ```sounddevice```
- ```soundfile```
- ```pyaudio```

To install all of these, you can use the ```requirements.txt``` file in the repo.  To do this, the command is:
```pip install -r requirements.txt```

I must iterate again, you must set up your API keys inside of ```key.txt```.  If you don't this won't work at all.  To get the openAI key, open up an account at https://openai.com/blog/openai-api and to get an Eleven Labs API key, you need to set-up an account at https://beta.elevenlabs.io/ (this is a paid option).

If you don't have python and git installed on your computer, check out this 5-minute tutorial I made here: https://youtu.be/Xk-u7tTqwwY
 
## Once you've done the previous stuff

Here's a quick description of the variables I reccommend be modified.  If you want to see how this is implemented in code, check out the python scripts in the assistants folder. 

```
# The only variables that need to be modifed
foldername = "assistantP"
personality = "assistantP"
voicename = "Rem"
useEL = False
usewhisper = True

script_dir = get_user_input()

foldername_dir, personality_dir, keys = get_file_paths(script_dir, 
                                                       foldername, 
                                                       personality)

chatbot = ChatGPT(personality=personality_dir, 
                  keys=keys, 
                  voice_name=voicename
                  )
chatbot.assistantP(save_foldername=foldername_dir,
                   useEL=useEL,
                   usewhisper=usewhisper
                   )

```

#### The 5 variables you can modify:

1. You set the ```foldername``` of where the conversations will be stored, this will be set in the conversations folder.
2. You set the ```personality``` by inputing the name of your text file and then editting the contents of the txt file name that is specified.  What this does is "prime" the ChatGPT conversation and sets the **personality** of the bot.  All of your prompts must go in the prompts folder and I have some examples in there already.
3. If you're using Eleven Labs for voice generation, change ```voicename``` to whatever voice you want that is available to you in Eleven Labs.
4. If you want to use Eleven Labs, change ```useEL``` to True
5. If you want to use Whisper instead of google voice recognition, change ```usewhisper``` to True.

The other text below the 5 variables are objects and function calls to set-up the voice assisant using the class and function in the voice_assistant module.

Most of the functions in the voice_assistant module have docstrings that you can read to clairfy what it does, but I'm still working on making it more clear.

## Working on / To-do's
- Incorporate long term memory, preferably local long term memory
- Change up winsound
