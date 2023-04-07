import os

def get_file_paths(script_dir:str, foldername:str, personality:str, system_change:str|None=None):
        foldername_dir = os.path.join(script_dir, f"conversations/{foldername}")
        personality_dir = os.path.join(script_dir, f"prompts/{personality}.txt")
        keys = os.path.join(script_dir, "keys.txt")
        if system_change:
            syschange_dir = os.path.join(script_dir, f"system_changes/{system_change}")
            return foldername_dir, personality_dir, keys, syschange_dir
        else:
            return foldername_dir, personality_dir, keys