import os
import random
import tempfile
import time
import typing
from typing import Dict, Optional

import numpy as np
import pyttsx3
import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write

recognizer = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty("voices")
for voice in voices:
    name = voice.name.lower()
    if "zira" in name or "female" in name:
        engine.setProperty("voice", voice.id)
        break

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

_TONE_RESPONSES = {
    "success": [
        "Done.",
        "Got it.",
        "All set.",
        "Expense recorded.",
    ],
    "info": [
        "Okay.",
        "Here you go.",
        "Let me tell you.",
    ],
    "error": [
        "Sorry, that failed.",
        "Hmm, something went wrong.",
        "I could not do that.",
    ],
    "summary": [
        "Here is the summary.",
        "Let me summarize.",
    ],
    "neutral": [""],
}

last_transcript: Optional[str] = None


def speak(text: str, tone: str = "neutral") -> None:
    if not text:
        return
    tone = tone or "neutral"
    prefix = random.choice(_TONE_RESPONSES.get(tone, [""]))
    utterance = f"{prefix} {text}" if prefix else text
    engine.say(utterance)
    engine.runAndWait()
    if len(utterance.split()) > 12:
        time.sleep(0.4)


def respond(action: str, message: str) -> None:
    tone_map = {
        "add": "success",
        "balance": "info",
        "recent": "info",
        "weekly": "summary",
        "monthly": "summary",
        "delete": "success",
        "error": "error",
        "help": "neutral",
        "repeat": "info",
    }
    speak(message, tone=tone_map.get(action, "neutral"))


def _record_audio(duration: float, fs: int) -> np.ndarray:
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    recording = np.asarray(recording)
    if recording.ndim > 1:
        recording = recording.squeeze(axis=1)
    return recording.astype(np.int16)


def get_voice_input(
    duration: float = 5.0,
    fs: int = 44100,
    language: str = "en-IN",
    retries: int = 1,
) -> str:
    global last_transcript
    attempt = 0
    while attempt <= retries:
        attempt += 1
        tmp_filename = None
        try:
            print(f"Recording for {duration} seconds…")
            recording = _record_audio(duration, fs)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_filename = tmp.name
            write(tmp_filename, fs, recording)

            with sr.AudioFile(tmp_filename) as source:
                audio = recognizer.record(source)

            transcript = recognizer.recognize_google(audio, language=language)
            transcript = transcript.strip()
            print("Heard:", transcript)
            last_transcript = transcript
            return transcript.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not catch that.", tone="error")
        except sr.RequestError as exc:
            speak("Speech service unavailable.", tone="error")
            print("Speech service error:", exc)
            break
        except sd.PortAudioError as exc:
            speak("Microphone error. Please check the device.", tone="error")
            print("Microphone error:", exc)
            break
        except Exception as exc:
            speak("I hit an unexpected problem.", tone="error")
            print("Voice input error:", exc)
        finally:
            if tmp_filename and os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)
                except OSError:
                    pass
    return ""


def parse_expense(text: str) -> Dict[str, typing.Any]:
    if not text or not text.strip():
        return {"action": "none"}

    text = text.lower()

    import re

    def extract_amount(raw: str) -> Optional[float]:
        match = re.search(r"([₹$€]?\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)", raw)
        if not match:
            return None
        cleaned = re.sub(r"[^\d\.-]", "", match.group(1))
        try:
            value = float(cleaned)
            return int(value) if value.is_integer() else value
        except ValueError:
            return None

    if re.search(r"\b(stop|exit|quit)\b", text):
        return {"action": "exit"}

    if re.search(r"\bhelp\b", text):
        return {"action": "help"}

    if re.search(r"\brepeat\b", text):
        return {"action": "repeat"}

    if re.search(r"\b(add|spent|record|put|note)\b", text):
        amount = extract_amount(text)
        category_match = re.search(
            r"(?:to|on|for|under)\s+([a-z0-9 ]+?)(?:[.,!?]| and |$)", text
        )
        category = (
            re.sub(r"[^\w\s]", "", category_match.group(1)).strip()
            if category_match
            else "uncategorized"
        )
        return {"action": "add", "amount": amount, "category": category}

    if re.search(r"\b(balance|total today|today)\b", text):
        return {"action": "balance"}

    if re.search(r"\b(recent|last)\b", text):
        return {"action": "recent"}

    if re.search(r"\bweekly\b", text):
        return {"action": "weekly"}

    if re.search(r"\bmonthly\b", text):
        return {"action": "monthly"}

    if re.search(r"\b(delete|remove|undo)\b", text):
        return {"action": "delete"}

    return {"action": "unknown", "raw": text}


def confirm_amount_flow(
    prompt_text: str = "Please say the amount now.",
    retries: int = 2,
) -> Optional[float]:
    speak(prompt_text)
    for _ in range(retries):
        follow_up = get_voice_input(duration=4)
        info = parse_expense(follow_up)
        amount = info.get("amount")
        if info.get("action") == "add" and amount is not None:
            return amount
        potential = info.get("raw") if info.get("raw") else follow_up
        try:
            return float(potential)
        except (TypeError, ValueError):
            speak("I still did not hear a number. Try again.", tone="error")
    return None


def repeat_last_transcript() -> Optional[str]:
    return last_transcript

