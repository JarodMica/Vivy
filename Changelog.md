# Changelog
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