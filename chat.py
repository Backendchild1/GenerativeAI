import sounddevice as sd
from openai import OpenAI
from scipy.io.wavfile import write
import keyboard
import time
import numpy as np
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to record audio
def record_audio():
    print('Press Enter to start recording... ')
    keyboard.wait('enter')
    print("Recording... Press Enter again to stop.")

    start_time = time.time()
    fs = 44100  # sample rate
    channels = 1  # use mono to avoid errors

    # record with float32 dtype
    recording = sd.rec(int(fs * 300), samplerate=fs, channels=channels, dtype="float32")

    keyboard.wait("enter")
    print("Stopping...")
    sd.stop()

    # duration
    duration = time.time() - start_time

    # convert float32 → int16
    recording = np.int16(recording * 32767)

    # save wav
    write("output.wav", fs, recording[:int(duration * fs)])
    print(f"Saved recording. Duration: {duration:.2f} seconds")
    print("File size:", os.path.getsize("output.wav"), "bytes")

# Function to transcribe audio
def speech_to_text():
    with open("output.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",  # try "whisper-1" if empty
            file=audio_file
        )
    print("RAW RESPONSE:", transcription)  # debug
    return getattr(transcription, "text", None)

# Loop to record and transcribe
def transcribe():
    while True:
        record_audio()
        output = speech_to_text()
        print("\n--- TRANSCRIPTION ---")
        print(output if output else "No text returned.")
        print("---------------------\n")

if __name__ == "__main__":
    transcribe()
