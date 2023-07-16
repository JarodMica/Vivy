import json
import os
import winsound
import sounddevice as sd
import soundfile as sf
import yaml
import simpleaudio as sa

def check_quit(user_input:str):
    if user_input.lower() == "quit" or "quit." in user_input.lower():
        raise SystemExit
    
def beep():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        beep_path = os.path.join(script_dir, "resources", "beep.mp3")
        data, samplerate = sf.read(beep_path)
        sd.play(data, samplerate)
    except:
        # If `soundfile` fails, play a system beep instead
        duration = 500
        frequency = 500
        winsound.Beep(frequency, duration)

# Moved over to yaml, but if json format is needed, replace .yaml with
# .json and use json.dump(messages, file, indent=4, ensure_ascii=False)
def get_suffix(save_foldername: str):
    '''
    Checks the folder for previous conversations and will get the next suffix that has not been used yet.

    Args:
        save_foldername (str) : Specify the name of the folder
    Returns:
        suffix (int) : Next unused suffix so the conversations don't all get stored in the same file
    '''
    
    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    suffix = 0
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.yaml')

    while os.path.exists(filename):
        suffix += 1
        filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.yaml')
    
    return suffix


def save_inprogress(messages, suffix, save_foldername):
    '''
    Uses the suffix number returned from save_conversation to continually update the 
    file for this instance of execution.  This is so that you can save the conversation 
    as you go so if it crashes, you don't lose to conversation.

    Args:
        suffix  :  Takes suffix count from save_conversation()
    '''

    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.yaml')

    with open(filename, 'w', encoding = 'utf-8') as file:
        yaml.dump_all(messages, file)

def filter_paragraph(paragraph, sentence_len = 130) -> tuple:
    '''
    Filters a large body of text into a list of strings to reduce the load
    sent over to the API.  Is needed to make the API calls faster and used for Tortoise

    Args:
        paragraph (str) : Any body of text
        sentence_len (int) : minimum length of sentence

    Returns:
        filtered_list (tuple) :  A list of sentences 

    '''
    paragraph = paragraph.replace('\n', ' ')  # Replace new lines with spaces
    sentences = paragraph.split('. ')
    filtered_list = []
    current_sentence = ""

    for sentence in sentences:
        if len(current_sentence + sentence) <= sentence_len:
            current_sentence += sentence + '. '
        else:
            if current_sentence.strip():  # Check if the current sentence is not just spaces
                filtered_list.append(current_sentence.strip())
            current_sentence = sentence + '. '

    if current_sentence.strip():  # Check if the current sentence is not just spaces
        filtered_list.append(current_sentence.strip())

    return filtered_list

def read_paragraph_from_file(file_path) -> str:
    with open(file_path, 'r') as file:
        paragraph = file.read()
    return paragraph

def play_audio(audio_path):
    try:
        data, samplerate = sf.read(audio_path)
        sd.play(data, samplerate)
        sd.wait()

    except:
        return "FIN"
    # os.remove(audio_path)

def async_play_audio(audio_path):
    data, sample_rate = sf.read(audio_path)
    channels = data.shape[1] if len(data.shape) > 1 else 1
    data = data.astype('float32')  # Convert the data to float32
    with sd.OutputStream(samplerate=sample_rate, channels=channels) as stream:
        stream.write(data)

    # os.remove(audio_path)



def get_path(name):
    '''
    Built to get the path of a file based on where the initial script is running
    
    Args:
        - name(str) : name of the file/folder
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, name)

def create_directory(name):
    '''
    Creates a directory based on the current scripts location. Relies on
    get_path()
    
    Args:
        - name(str) : name of the file/folder
    '''
    dir_name = get_path(name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)