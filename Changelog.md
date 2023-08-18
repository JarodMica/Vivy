# Changelog

## 8/18/2023
Removed manual RVC installation, instead, now using the packaged version on my Github.  Run through the installation there.
- Modifed the generate_voice function in Kokoro to now use rvc_convert, everything is handled there in the package
    - Note to self: functions pretty much the same, but still need to check for bugs
- Added a rvc_model_path parameter that is now necessary in order to run an RVC voice.  This needs to get placed inside of the rvc_model folder which is located at the top most level directory at the current moment
- rmvpe.pt and hubert_base.pt NEED to be placed in the top most level directory for RVC to work.

## 7/16/2023
Made some enhancements for the AI Streamer and tried off stream, but the generations were STUPID slow.  Originally, I had it done in another queue and this queue was closed after running RVC.  This caused RVC to be unloaded each time, making it take SOO long.  I was wondering why it worked so well in assistantp.py after it started going and this was why...
- The queue now is instantiated in the __init__ part of kokoro along with the other queues.  Then, when it's needed I check inside of generate_voice if the queue has already been started and if not, it'll start this queue.
- Then the only thing that is needed is to put audio into the process queue... so it's in an infinite queue.  Zombies perhaps, but just getting things works lol.
- For this, a new function rvc_queue() was created which is what stays alive for this queue to run on in the background
### Observations & notes
- There is a weird issue that occurs where the voice goes DEEP for some reason... I need to check this out.
- In retrospec, I should've made the "assistants" folder the parent folder...... but it's ok


## 7/14/2023
Continuing work on the RVC integration, this caused me a huge headache today as this is way over my head at the moment.
- The AI_Streamer class is heavily reliant upon threads and before, this was OKAY because I wasn't trying to run any heavy processes on it.  ですが, RVC inference seems to be heavily CPU based, so when trying to fulfill this request in a single core, the script was taking WAY too long to produce an audio sample and I'm assuming this is due to the GIL not actually being true paralellism in threading.
- The solution to this is to run the rvc_run() function inside of Kokoro.generate_voice in a separate process using multiprocess instead rather than allowing it to just run via the ai_streamer.py's own tts_generation() function.
- I'm assuming this now moves it over to another core to the the processing so that it's not split between like 15 different threads on a sigle core
- As well, I tried converting everything to multiprocessing, but this was the cause of the headache because of some pickling issue, etc.  Unfortunately, my knowledge is not deep enough in this area to understand the full reasoning.


## 7/9/2023
Starting to work on integrating RVC into the pipeline for tortoise, some notes to take:
- Added an ```rvc``` folder into the ```package``` that can be installed by navigating into the RVC directory with ```pip install -e .```.  The current commit # for RVC is: 211e13b80a4bf13d683f199d75a2f88dd50b7444
    - Going back to my notes, I deleted the pyproject.toml file and created a basic setup.py file to make it installable (the toml file was creating issues as that's for the poetry install)
    - The folder was renamed rvc after cloning it
    - To actually install it, you'll need all of the RVC requirements already installed
- Added an ```rvc_infer.py``` file that can be used to convert audio into an RVC trained voice based on myinferer.py from the RVC HF
- Added an ```rvc.yaml``` file that is used to configure RVC settings
- Changed up the audio generation logic in ```generate_voice``` as it wasn't working as I had intended for tortoise and rvc.  Ended up needing to open up async_play in another thread and putting audio paths into a queue to be played
- 
### Some Thoughts
- May need to configure the requirements to exclude torch if user does not want to run with RVC as these are some hefty files


## 6/15/2023
The major change here was the refactoring and moving around of functions/methods, but overall, everything works pretty much exactly the same as before.
- Refactored the code to reduce the amount of parameters being passed over into each individual assistant class.  Instead, a bulk majority of that is now instantiated when calling the main kokoro class
    - This can be seen in something like response_completion() where I moved the exception handling to be inside here instead of the assistant classes
- Re-thought over certain variables, the largest being the TTS generation.  Before, there bool variables like useEL & useTortoise which would be difficult to handle with more engines, so now it's just specified by doing tts = "name".  This will make it easier to add other tts engines like Azure etc.
- Moved additional functions into assistant_utils to organize utility functions
- Add additional methods inside of kokoro to handle logic that was being repeated in the assistant classes.  This will make it easier to simply just call the name of the method instead of passing 5 billion paramters into each method call.
- misc. clean up of the 
- Removed updatein from the chat assistant, I don't think it's that useful of a feature anymore to inject a new prompt into the assistant mid-way through so I will be removing that from chat.py
- Removed system_change in interview assistant.  Same reasoning as chat assistant essentially.
- Removed the logic to determine if being ran as a script or exe file in the assistant scripts
- Removed one_up.py and roleplay.py from the assistants folder as it's additional work to have to maintain across changes and they're fundamentally identical to other scripts.  The reason being is they are just a modification of the personality and foldername variables.  one_up.py relies on the assistant class and roleplay relies on the chat class and the variables just need to be changed accordingly
- Froze package requirements to hopefully keep things more stable across installations

### Some thoughts
- Might need some type of flag in the future to let the assistant class "know" that the list of dictionaries for the responses has been reset due to maximum token count
- Some classifications to understand what is being referred to... 
    - assistant *scripts* are the main scripts you run based on the "type" you want
    - assistant *classes* are the modules in the package directory that contain the logic of each of these assistants and how they function