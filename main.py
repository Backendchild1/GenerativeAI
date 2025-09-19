import sounddevice as sd
from scipy.io.wavfile import write
import keyboard
import time
import numpy as np
import os
from faster_whisper import WhisperModel

# Load faster-whisper model
model = WhisperModel("base", device="cpu", compute_type="int8")

def record_audio():
    print("Press Enter to start recording...")
    keyboard.wait("enter")
    print("Recording... Press Enter again to stop.")

    fs = 44100
    channels = 1
    frames = []

    with sd.InputStream(samplerate=fs, channels=channels, dtype="float32") as stream:
        while not keyboard.is_pressed("enter"):
            data, _ = stream.read(1024)
            frames.append(data)

    recording = np.concatenate(frames, axis=0)
    write("output.wav", fs, recording)  # keep float32
    print(f"Saved recording ({len(recording)/fs:.2f} sec)")

def speech_to_text():
    segments, info = model.transcribe("output.wav", language="en", beam_size=1)
    text = " ".join([seg.text for seg in segments])
    print(f"Detected language: {info.language}")
    return text.strip()

def transcribe():
    while True:
        record_audio()
        output = speech_to_text()
        print("Transcription:", output if output else "No text detected.")

if __name__ == "__main__":
    transcribe()
