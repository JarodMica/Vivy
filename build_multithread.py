import subprocess
import glob
import os
import shutil
import concurrent.futures

assistants = ['one_up', 'roleplay', 'interview', 'assistantp', 'assistant', 'chat']
assistants_path = "assistants"
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)

distpath = os.path.join(current_dir, assistants_path)

def compile_assistant(assistant):
    cmd = ["pyinstaller",
           "--onefile",
            "--distpath=" f"{distpath}",
            f"{assistants_path}/{assistant}.py"]
    subprocess.run(cmd, shell=False)

if __name__ == '__main__':
    # Add freeze_support() for Windows platforms
    if os.name == 'nt':
        from multiprocessing import freeze_support
        freeze_support()
    
    # Process all assistants in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(compile_assistant, assistant) for assistant in assistants]

    # Delete all .spec files in the current directory
    for spec_file in glob.glob("*.spec"):
        os.remove(spec_file)
    # Removes build folder (if you don't want this, you can comment this out)
    shutil.rmtree("build")

    input("Press Enter to continue...")
