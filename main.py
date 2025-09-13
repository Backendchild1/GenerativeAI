import sounddevice as sd
from scipy.io.wavfile import write
import keyboard
import time
import numpy as np
import os
from faster_whisper import WhisperModel

# Load faster-whisper model (options: tiny, base, small, medium, large)
# "tiny" is fastest but less accurate, "base" is a good balance
model = WhisperModel("base", device="cpu", compute_type="int8")
# If you have a GPU, change to: device="cuda", compute_type="float16"

# Function to record audio
def record_audio():
    print('Press Enter to start recording... ')
    keyboard.wait('enter')  # wait for first Enter
    print("Recording... Press Enter again to stop.")

    start_time = time.time()  # start timestamp
    fs = 44100  # sample rate
    channels = 1  # mono to avoid channel errors

    # record with float32
    recording = sd.rec(int(fs * 300), samplerate=fs, channels=channels, dtype="float32")

    keyboard.wait("enter")  # wait for second Enter
    print("Stopping...")
    sd.stop()

    # calculate duration
    duration = time.time() - start_time

    # convert to int16 before saving
    recording = np.int16(recording * 32767)

    # save recording
    write("output.wav", fs, recording[:int(duration * fs)])
    print(f"Saved recording. Duration: {duration:.2f} seconds")
    print("File size:", os.path.getsize("output.wav"), "bytes")

# Function to transcribe audio
def speech_to_text():
    segments, info = model.transcribe("output.wav", beam_size=5)
    text = " ".join([segment.text for segment in segments])
    print(f"Detected language: {info.language}")
    return text.strip()

# Loop to record and transcribe
def transcribe():
    while True:
        record_audio()
        output = speech_to_text()
        print()
        print(output if output else "No text detected.")
        print()

if __name__ == "__main__":
    transcribe()
