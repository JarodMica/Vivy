# QUICK DESCRIPTION:

This repo utilizes OpenAI's GPT-3.5 Turbo model to engage in personalized conversations with users, catering to their preferred communication style. As GPT-3.5 Turbo serves as the foundation for ChatGPT, this project essentially shares its underlying model. Ultimately, the aim of this project is to develop a personal assistant that emulates human-like interactions. As the project is a work in progress, its features will expand as I continue to refine and iterate on the concept.

The fastest way to try these assistants would be to setup your API keys in the ```key.yaml``` file and then run the exe files I have provided.  For this to work, **you must** rename ```keys_example.yaml``` to be ```keys.yaml```.  To find the exe files, check the latest release for this project https://github.com/JarodMica/Vivy/releases/

## Features
:heavy_check_mark: Voice recognition and voice responses

:heavy_check_mark: Integration with ChatGPT for responses and ElevenLabs for natural sounding text-to-speech

:heavy_check_mark: Easy customization for personalities of the AI assistants, with funtionality variations of the assistants

:heavy_check_mark: Local conversation history stored for future reference

## Working on / To-do's
- [ ] Currently some bugs with the exe files that I'm not able to trace entirely.  Issue [#11](https://github.com/JarodMica/Vivy/issues/11)
 is tracking it
- [ ] Incorporate long term memory, preferably local long term memory
- [ ] Add some functionality to be useful like assistants seen in movies :)

## YouTube Tutorial 
Most recent: https://youtu.be/0qpar5R1VA4

## EXE Quick Use

If you just want to try out the assistants, download the zip folder and then unzip it to any location on your PC. Once unzipped, rename the keys_example file to ```keys.yaml``` and then set up your API Keys in ```key.yaml```. Now you can do two things, run the exe and try it out or adjust the prompts in the prompts folder.  If you run interview.exe, it's going to use the interview.txt file (same with roleplay). Else, you can modify the prompts to your own case and then run the exe files.

## How to run it in python:
You'll need Git, Python, and I recommend some type of IDE like VSCode.  I have a 5-minute tutorial here **BUT BEWARE, I show python 3.11, you need 3.10 for Vivy**: https://youtu.be/Xk-u7tTqwwY

Once you have those things installed, open a terminal window and clone the repo:
```
git clone https://github.com/JarodMica/Vivy.git
```

**Note:** I highly recommend looking into doing this as a virtual environment (venv) so that you don't have any issues in the future if you're installing other python projects, go watch this here: https://www.youtube.com/watch?v=q1ulfoHkNtQ.  

That being said, if you just wanna run this project real quick, you can follow below (make sure you didn't close the terminal after cloning the repo):
```
cd Vivy
pip install -r requirements.txt
```
Now navigate into the assistants folder and then choose a python script to run, ```dir``` will list all of the scripts in the folder:
```
cd assistants
dir
python assistantp.py
```

And boom! The script should be running.

Once again, make sure your API keys inside of ```key.yaml``` are set-up.  If you don't do this, it won't work at all.  To get the openAI key, open up an account at https://openai.com/blog/openai-api and to get an Eleven Labs API key, you need to set-up an account at https://beta.elevenlabs.io/ (this is a paid option).
 
## If you're running in Python

Here's a quick description of the variables I reccommend be modified.  If you want to see how this is implemented in code, check out the python scripts in the assistants folder.  You'll find these at the top of the python script.

```
foldername = "assistantP"
personality = "assistantP"
voicename = "Rem"
useEL = False
usewhisper = True
```

#### The 5-ish variables you can modify:

1. You set the ```foldername``` of where the conversations will be stored, this will be set in the conversations folder.
2. You set the ```personality``` by inputing the name of your text file and then editting the contents of the txt file name that is specified.  What this does is "prime" the ChatGPT conversation and sets the **personality** of the bot.  All of your prompts must go in the prompts folder and I have some examples in there already.
3. If you're using Eleven Labs for voice generation, change ```voicename``` to whatever voice you want that is available to you in Eleven Labs.
4. If you want to use Eleven Labs, change ```useEL``` to True
5. If you want to use Whisper instead of google voice recognition, change ```usewhisper``` to True.

The other text below the 5 variables in the script are objects and function calls to set-up the voice assisant using the class and function in the voice_assistant module.

Most of the functions in the voice_assistant module have docstrings that you can read to clairfy what it does, but I'm still working on making it more clear.

