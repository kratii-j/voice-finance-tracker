import sounddevice as sd
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile, os
import pyttsx3
import re

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_voice_input(duration=5, fs=44100):
    print(f"Speak your command (recording for {duration} seconds)...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmp_filename = tmpfile.name

    write(tmp_filename, fs, recording)

    with sr.AudioFile(tmp_filename) as source:
        audio = recognizer.record(source)

    os.remove(tmp_filename)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, could not understand the audio.")
        return ""
    except sr.RequestError as e:
        speak(f"Could not request results; {e}")
        return ""

def add_expense_nlp(text):
    keywords = ["add", "spent", "record", "put"]
    if any(w in text for w in keywords):
        amount_match = re.search(r'\d+', text)
        amount = int(amount_match.group()) if amount_match else 0
        category_match = re.search(r'(?:to|on)\s+([\w\s]+)', text)        
        category = category_match.group(1).strip() if category_match else "uncategorized"
        return amount, category
    return None, None

if __name__ == "__main__":
    speak("Voice assistant ready. Say a command or say stop to quit.")

    MAX_ATTEMPTS = 5
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        user_text = get_voice_input(duration=5)

        if not user_text:
            attempts += 1
            print(f"No input detected. Attempt {attempts} of {MAX_ATTEMPTS}")
            continue

        attempts = 0

        exit_commands = ["stop", "exit", "quit"]
        if any(cmd in user_text for cmd in exit_commands):
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
