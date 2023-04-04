import os
import sys

def get_user_input():
    if getattr(sys, 'frozen', False):
        # running as a compiled executable
        script_dir = os.path.dirname(os.path.abspath(sys.executable))
        while True:
            user_input = input("Are you using an Eleven Labs voice (yes/no)?\n")
            if user_input == 'yes':
                voicename = input("What is the name of you Eleven Labs voice: ")
                useEL = True
                break
            elif user_input == 'no':
                break
            else:
                print("Invalid Input, please try again.")
    else:
        # running as a script file
        script_dir = os.path.dirname(os.path.abspath(__file__))

    return script_dir

def get_file_paths(script_dir:str, foldername:str, personality:str, system_change:str|None=None):
        foldername_dir = os.path.join(script_dir, f"conversations/{foldername}")
        personality_dir = os.path.join(script_dir, f"prompts/{personality}.txt")
        keys = os.path.join(script_dir, "keys.txt")
        if system_change:
            syschange_dir = os.path.join(script_dir, f"system_changes/{system_change}")
            return foldername_dir, personality_dir, keys, syschange_dir
        else:
            return foldername_dir, personality_dir, keys