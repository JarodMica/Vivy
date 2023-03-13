# QUICK DESCRIPTION:

This repo utilizes OpenAI's GPT-3.5 Turbo model to engage in personalized conversations with users, catering to their preferred communication style. As GPT-3.5 Turbo serves as the foundation for ChatGPT, this project essentially shares its underlying model. Ultimately, the aim of this project is to develop a personal assistant that emulates human-like interactions. As the project is a work in progress, its features will expand as I continue to refine and iterate on the concept.

The fastest way to try these assistants would be to setup your API keys in the ```key.txt``` file and then run the exe files I have provided.  For this to work, **you must** rename ```keys_example.txt``` to be ```keys.txt```.  To find the exe files, check the latest release for this project https://github.com/JarodMica/Vivy/releases/tag/v0.1.0-alpha.

## EXE Quick Use

If you just want to try out the assistants, download the zip folder and then unzip it to any location on your PC. Once unzipped, rename the keys txt file to ```keys.txt``` and then set up your API Keys in ```key.txt```. Now you can do two things, run the exe and try it out or adjust the prompts in the prompts folder.  If you run interview.exe, it's going to use the interview.txt file (same with roleplay). Else, you can modify the prompts to your own case and then run the exe files.

## How the assistant currrently works:
In general, this is how it work:
1. Run python script and it will start with "Initializing".  Now it's in a "listening" state.
2. The AI assistant is activated when the user says "hey" or anything containing this keyword ("they" does not work)
3. Now the user can speak to the AI, it'll listen until you stop speaking (default is 0.8 seconds)
4. It then transcribes the user's speech and generates a response using ChatGPT
5. It will read out the response.
6. The conversation history is saved to a file in a specified folder and the program loops.

If you say quit, it will quit.

#### The following libraries are required to run the ChatGPT class:
- ```pip install SpeechRecognition```
- ```pip install elevenlabslib```
- ```pip install openai```
- ```pip install pyttsx3```
- ```pip install sounddevice```
- ```pip install soundfile```
- ```pip install pyaudio```

I must iterate again, you must set up your API keys inside of ```key.txt```.  If you don't this won't work at all.  To get the openAI key, open up an account at https://openai.com/blog/openai-api and to get an Eleven Labs API key, you need to set-up an account at https://beta.elevenlabs.io/ (this is a paid option).

(additionally, if you don't have python installed on your device, there are a bajillion tutorials on youtube to how to do this, so go check those out if you don't have it installed!)

## Once you've done the previous stuff

Here's a quick description of the variables I reccommend be modified.  If you want to see how this is implemented in code, check out the python scripts in the assistants folder. 

```
# The only variables that need to be modifed
foldername = "assistant"
personality = "assistant"
voicename = "Rem"
useEL = False
usewhisper = True
```

#### What is happening here and how to modify it to your own assistant:
1. You set the ```personality``` by inputing the name of your text file and then editting the contents of the txt file name that is specified.  What this does is "prime" the ChatGPT conversation and sets the **personality** of the bot.  All of your prompts must go in the prompts folder and I have some examples in there already.
2. If you're using Eleven Labs for voice generation, change ```voicename``` to whatever voice you want that is available to you in Eleven Labs.
3. Change ```foldername``` to whatever folder name you want your conversations to be stored as.  It will be placed in a "conversations" folder where you will find the name of you folder in.
4. Determine whether or not you want to use Eleven Labs with ```useEL```.  It defaults to False, but I have it there as a varibale so that it can easily be changed.
5. ```usewhisper``` determines if you want to use Whisper as the transcription service as opposed to google.  Works better in my opinion but costs more tokens.  I set to True here, but it defaults to False.

And that's basically it if you just wanna use the chat function.  There are some additional parameters and methods that are included in the class but not in this example, but until I come up with some better documentation, I'll have to leave it at this for now.

As well, you can look at the class and how its methods work; there are docstrings in the class.  I'm working on making it more clear, but if you don't understand what is happening, just feed it into chatGPT and ask it what the code does.
