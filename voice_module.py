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
