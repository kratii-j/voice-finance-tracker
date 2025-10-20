import sounddevice as sd
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile, os
import pyttsx3
import re
import random
import time
import logging
import typing

engine = pyttsx3.init()
voices = engine.getProperty("voices")
recognizer = sr.Recognizer()

for v in voices:
    if "female" in v.name.lower() or "zira" in v.name.lower():
        engine.setProperty("voice", v.id)
        break

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

def speak(text: str, tone: str = "neutral"):
    """Speak text with an optional tone prefix. tone defaults to 'neutral'."""
    if not text:
        return

    # ensure tone fallback
    tone = tone or "neutral"

    responses = {
        "success": [
            "Done!",
            "Got it!",
            "Alright, noted.",
            "All set.",
            "Expense recorded successfully."
        ],
        "error": [
            "Sorry, something went wrong.",
            "Hmm, that didn't work.",
            "Couldn't do that right now.",
        ],
        "info": [
            "Here's what I found.",
            "Okay, just a second.",
            "Fetching that for you.",
        ],
        "summary": [
            "Here's your summary.",
            "Let me tell you what I found.",
            "Here's an overview.",
        ],
        "neutral": [""],
    }

    prefix = random.choice(responses.get(tone, [""]))
    full_text = f"{prefix} {text}" if prefix else text

    engine.say(full_text)
    engine.runAndWait()

    # small pause for long messages
    if len(text.split()) > 10:
        time.sleep(0.5)

def respond(action, message):
    tone_map = {
        "add": "success",
        "balance": "info",
        "summary": "summary",
        "recent": "info",
        "delete": "success",
        "error": "error",
        "help": "neutral",
    }
    tone = tone_map.get(action, "neutral")
    speak(message, tone=tone)


# add a small in-memory history for last transcript
last_transcript: typing.Optional[str] = None

def get_voice_input(duration=5, fs=44100, language="en-IN", retries=1):
    """
    Record audio using sounddevice, save to a temporary WAV, transcribe with Google ASR.
    - retries: how many additional attempts to try when recognition fails.
    - language: passed to recognizer.recognize_google()
    Returns recognized text (lowercased) or empty string on failure.
    Also stores the last successful transcript in last_transcript.
    """
    global last_transcript
    attempts = 0
    while attempts <= retries:
        print(f"Speak your command (recording for {duration} seconds)... (attempt {attempts+1}/{retries+1})")
        tmp_filename = None
        try:
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()

            recording = np.asarray(recording)
            if recording.ndim > 1 and recording.shape[1] == 1:
                recording = recording.squeeze(axis=1)
            recording = recording.astype(np.int16)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                tmp_filename = tmpfile.name

            write(tmp_filename, fs, recording)

            with sr.AudioFile(tmp_filename) as source:
                audio = recognizer.record(source)

            text = recognizer.recognize_google(audio, language=language)
            print("You said:", text)
            text = text.strip()
            if text:
                last_transcript = text.lower()
                return last_transcript
            # fallback to next attempt
            attempts += 1
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.", tone="error")
            attempts += 1
            continue
        except sr.RequestError as e:
            logging.error("Recognition service error: %s", e)
            speak("Speech recognition service unavailable.", tone="error")
            break
        except sd.PortAudioError as e:
            logging.error("PortAudio error: %s", e)
            speak("Audio device error. Check your microphone.", tone="error")
            break
        except Exception as e:
            logging.exception("Voice input error")
            speak("An error occurred while recording.", tone="error")
            break
        finally:
            if tmp_filename and os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)
                except OSError:
                    pass

    return ""

def parse_expense(text: str) -> dict:
    """
    Improved parsing:
    - Accepts currency symbols, commas, decimals and negatives.
    - Non-greedy category capture; stops at punctuation or common conjunctions.
    Returns dict: {"action": "...", ...}
    """
    if not text or not text.strip():
        return {"action": "none"}

    text = text.lower()

    # quick commands
    if re.search(r'\b(stop|exit|quit)\b', text):
        return {"action": "exit"}
    if re.search(r'\bhelp\b', text):
        return {"action": "help"}
    if re.search(r'\b(repeat|say that again|what did you say)\b', text):
        return {"action": "repeat"}
    if re.search(r'\b(what did i say|last said)\b', text):
        return {"action": "what_i_said"}

    # add / spend intent
    if re.search(r'\b(add|spent|spend|record|put)\b', text):
        # amount: optional currency symbol, optional negative, supports commas and decimals
        amt_pat = r'([₹$€]?\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
        amount_match = re.search(amt_pat, text)
        amount = None
        if amount_match:
            amt_str = amount_match.group(1)
            # sanitize: remove currency and commas but keep negative and decimal point
            amt_str = re.sub(r'[^\d\.-]', '', amt_str)
            try:
                amount = float(amt_str) if '.' in amt_str or '-' in amt_str else int(float(amt_str))
            except ValueError:
                amount = None

        # category: capture after to/on/for/in and stop at punctuation or common conjunctions (and/with/for)
        cat_pat = r'(?:to|on|for|in)\s+(.+?)(?=(?:\s+(?:and|with|or|for|at|in)\b|[.,!?]|$))'
        category = "uncategorized"
        cat_m = re.search(cat_pat, text)
        if cat_m:
            category = cat_m.group(1).strip()
            category = re.sub(r'[^\w\s\-&]', '', category)  # keep letters, numbers, spaces, - &

        return {"action": "add", "amount": amount, "category": category}

    # other intents
    if re.search(r'\b(balance|total today|today|show balance)\b', text):
        return {"action": "balance"}
    if re.search(r'\b(recent|last|show recent)\b', text):
        return {"action": "recent"}
    if re.search(r'\bweekly\b', text):
        return {"action": "weekly"}
    if re.search(r'\bmonthly\b', text):
        return {"action": "monthly"}
    if re.search(r'\b(delete|remove|erase)\b', text):
        return {"action": "delete"}

    return {"action": "unknown"}

def confirm_amount_flow(prompt_text: str = "I did not catch the amount. Please say the amount now.", retries: int = 2):
    """
    If parser couldn't find an amount, prompt the user and try to capture just the amount.
    Returns the parsed amount (int/float) or None.
    """
    speak(prompt_text, tone="info")
    reply = get_voice_input(duration=4, retries=retries)
    if not reply:
        return None
    parsed = parse_expense(reply)
    if parsed.get("action") == "add":
        return parsed.get("amount")
    # try to extract numeric token directly
    m = re.search(r'([₹$€]?\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)', reply)
    if m:
        s = re.sub(r'[^\d\.-]', '', m.group(1))
        try:
            return float(s) if '.' in s or '-' in s else int(float(s))
        except ValueError:
            return None
    return None

def repeat_last_transcript():
    """Return the last recognized transcript (raw, not lowercased) or empty string."""
    return last_transcript or ""

