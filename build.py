import subprocess
import glob
import os

assistants = ['one_up', 'roleplay', 'interview', 'assistantp', 'assistant']
distpath = 'assistants'

for assistant in assistants:
    cmd = f"pyinstaller --onefile --distpath={distpath} {assistant}.py"
    subprocess.run(cmd, shell=True)

# Delete all .spec files in the current directory
for spec_file in glob.glob("*.spec"):
    os.remove(spec_file)

input("Press Enter to continue...")