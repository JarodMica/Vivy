import json
import os
import sounddevice as sd
import soundfile as sf

def check_quit(user_input:str):
    if user_input.lower() == "quit" or "quit." in user_input.lower():
        raise SystemExit
    
def beep():
        data, samplerate = sf.read("assistants\\package\\resources\\beep.mp3")
        sd.play(data, samplerate)

def save_conversation(messages, save_foldername:str):
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
        json.dump(messages, file, indent=4, ensure_ascii=False)

    return suffix

def save_inprogress(messages, suffix, save_foldername):
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
        json.dump(messages, file, indent=4, ensure_ascii=False)