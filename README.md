# QUICK DESCRIPTION:

The personal_assistant repo utilizes OpenAI's GPT-3.5 Turbo model to engage in personalized conversations with users, catering to their preferred communication style. As GPT-3.5 Turbo serves as the foundation for ChatGPT, this project essentially shares its underlying model. Ultimately, the aim of this project is to develop a personal assistant that emulates human-like interactions. As the project is a work in progress, its features will expand as I continue to refine and iterate on the concept.

## How the assistant currrently works:
In general, this is how it work:
1. Run python script and it will start with "Initializing".  Now it's in a "listening" state.
2. The AI assistant is activated when the user says "hey" or anything containing this keyword (they does not work)
3. Now the user can speak to the AI, it'll listen until you stop speaking (default is 0.8 seconds)
4. It then transcribes the user's speech and generates a response using ChatGPT
5. It will read out the response.
6. The conversation history is saved to a file in a specified folder and the program loops.

If you say quit, it will quit.

#### The following libraries are required to run the ChatGPT class:
- speech_recognition ```pip install SpeechRecognition```
- elevenlabslibos ```pip install elevenlabslib```
- openai ```pip install openai```
- pyttsx3 ```pip install pyttsx3```

As well, you will need to have an ``` import key ``` line as well in order to import your API keys.

Here's a quick example of a python script that works with the ChatGPT class defined in gpt_assistant:
```
import os
from gpt_assistant import ChatGPT

# Set-up personality, profession, or specialty of the bot
current_directory = os.getcwd()
personality = "roleplay.txt"
directory = os.path.join(current_directory,'prompts', personality)

# Set-up Eleven Labs voice
voicename = "Rem"

# name of folder to save conversations into
save_foldername = "rem"

# The magic bot:
chatbot = ChatGPT(directory, voicename)
chatbot.chat(save_foldername, useEL = False)

```

#### What is happening here and how to modify it to your own assistant:
1. You set the ```personality``` by inputing the name of your text file and then editting the contents of the txt file name that is specified.  What this does is "prime" the gpt-3.5 conversation and sets the **personality** of the bot.  All of your prompts must go in the prompts folder and I have some examples in there already.
2. If you're using Eleven Labs for voice generation, change ```voicename``` to whatever voice you want that is available to you in Eleven Labs.
3. Change ```save_foldername``` to whatever folder name you want your conversations to be stored as.  It will be placed in a "conversations" folder where you will find the name of you folder in.

And that's basically it if you just wanna use the chat function.  There are some additional parameters and methods that are included in the class but not in this example, but until I come up with some better documentation, I'll have to leave it at this for now.

As well, you can look at the class and how its methods work; there are docstrings in the class.  I'm working on making it more clear, but if you don't understand what is happening, just feed it into chatGPT and ask it what the code does.
