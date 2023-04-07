import os
import glob

os.system("pyinstaller --onefile --distpath=assistants\\ assistants\\one_up.py")
os.system("pyinstaller --onefile --distpath=assistants\\ assistants\\roleplay.py")
os.system("pyinstaller --onefile --distpath=assistants\\ assistants\\interview.py")
os.system("pyinstaller --onefile --distpath=assistants\\ assistants\\assistantp.py")
os.system("pyinstaller --onefile --distpath=assistants\\ assistants\\assistant.py")

# Delete all .spec files in the current directory
for spec_file in glob.glob("*.spec"):
    os.remove(spec_file)

input("Press Enter to continue...")
