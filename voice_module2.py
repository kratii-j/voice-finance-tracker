<<<<<<< HEAD
import pyttsx3
import speech_recognition as sr
import re
import sys

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_voice_input(timeout=5, phrase_time_limit=5):
    """Listen once, return text, or '' on timeout/error."""
    try:
        with sr.Microphone() as source:
            print(f"Listening (start within {timeout}s)...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            try:
                text = recognizer.recognize_google(audio)
                print("You said:", text)
                return text.lower()
            except sr.UnknownValueError:
                print("Could not understand audio.")
                return ""
            except sr.RequestError:
                print("Speech recognition service error.")
                return ""
    except sr.WaitTimeoutError:
        print("Listening timed out (no speech detected).")
        return ""
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return "exit"  # treat Ctrl+C as exit

def add_expense_nlp(text):
    keywords = ["add", "spent", "record", "put"]
    if any(w in text for w in keywords):
        amount_match = re.search(r'\d+', text)
        amount = int(amount_match.group()) if amount_match else 0
        category_match = re.search(r'(?:to|on)\s+(\w+)', text)
        category = category_match.group(1) if category_match else "uncategorized"
        return amount, category
    return None, None

# main loop
speak("Voice assistant ready. Say a command or say stop to quit.")

MAX_ATTEMPTS = 5
attempts = 0

while attempts < MAX_ATTEMPTS:
    user_text = get_voice_input(timeout=5, phrase_time_limit=5)

    if not user_text:
        attempts += 1
        print(f"No input detected. Attempt {attempts} of {MAX_ATTEMPTS}")
        continue

    attempts = 0

    if "stop" in user_text or "exit" in user_text or "quit" in user_text:
        speak("Stopping the voice assistant. Goodbye.")
        print("Exiting.")
        break

    amount, category = add_expense_nlp(user_text)
    if amount:
        speak(f"Adding {amount} rupees to {category}")
        print(f"Add expense: {amount}, category: {category}  (call backend here)")
    elif "balance" in user_text:
        speak("Showing balance.")
        print("Show balance (call backend here)")
    elif "recent" in user_text or "last" in user_text:
        speak("Showing recent transactions.")
        print("Show recent transactions (call backend here)")
    else:
        speak("Command not recognized. Say help for options.")
        print("Command not recognized.")

if attempts >= MAX_ATTEMPTS:
    speak("No command received. Exiting the assistant.")
    print("No input received after multiple attempts. Exiting.")
=======
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile, os
import pyttsx3
import re

# Initialise Text-To-Speech Engine
engine=pyttsx3.init()

def get_voice_input(duration=5,fs=44100):
    recognizer = sr.Recognizer()

    print(f"Speak Your Expense (recording for {duration} seconds)")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    # Create a temp WAV file and close it immediately so scipy can write to it
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmp_filename = tmpfile.name

    # Save recording to the temp WAV file
    write(tmp_filename, fs, recording)

    # Use SpeechRecognition to process the WAV
    with sr.AudioFile(tmp_filename) as source:
        audio = recognizer.record(source)

    # Clean up the temp file
    os.remove(tmp_filename)

    # Convert speech to text
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak_output( "Sorry, could not understand the audio")
        return ""
    except sr.RequestError as e:
        speak_output(f"Could not request results; {e}")
        return ""


def parse_expense(text):
    amount=0
    category="others"
    
    numbers=re.findall(r"\d+",text)
    if numbers:
        amount=int(numbers[0])
        
    match=re.search(r'on (\w+)',text.lower())
    if match:
        category=match.group(1)
        
    if not numbers:
        return None, category
        
    return amount, category


# Speaks Text
def speak_output(text):
    engine.say(text)
    engine.runAndWait()
    
    
    
if __name__ == "__main__":
    while True:
        text = get_voice_input()
        if "exit" in text.lower():
            speak_output("Goodbye")
            print("Goodbye")
            break
        if text:
            amount, category = parse_expense(text)
            print(f"Amount: {amount}, Category: {category}")
            speak_output(f"Noted: {amount} added to {category}")
        else:
            speak_output("Could not understand your input. Please try again.")
>>>>>>> b659663cad118576d7116a695b89e589ab91ab8c
