import os
import sounddevice as sd
import numpy as np
import threading
import wave
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)

# Load API key
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

deepgram = DeepgramClient(DEEPGRAM_API_KEY)
dg_connection = deepgram.listen.websocket.v("1")

# Store transcript + audio frames
all_transcripts = []
audio_frames = []

# Callback for transcription
def on_message(self, result, **kwargs):
    sentence = result.channel.alternatives[0].transcript
    if sentence:
        all_transcripts.append(sentence)
        print("Transcript:", sentence)

dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

# Deepgram config
options = LiveOptions(
    model="nova-3",
    language="en",
    encoding="linear16",
    sample_rate=16000,
)

if dg_connection.start(options) is False:
    print(" Failed to start connection")
    exit(1)

# Microphone streaming
def mic_stream():
    with sd.InputStream(samplerate=16000, channels=1, dtype="int16") as stream:
        print("🎤 Speak into your mic (Ctrl+C to stop)...")
        while True:
            data, _ = stream.read(1024)
            audio_bytes = data.tobytes()
            dg_connection.send(audio_bytes)
            audio_frames.append(audio_bytes)  # save for output.wav

# Run
try:
    t = threading.Thread(target=mic_stream)
    t.start()
    t.join()
except KeyboardInterrupt:
    print("\nStopping...")

    # ✅ Stop connection
    dg_connection.finish()

   
    with wave.open("output.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 → 2 bytes
        wf.setframerate(16000)
        wf.writeframes(b"".join(audio_frames))
    print("💾 Saved recording as output.wav")

    # ✅ Save transcript
    full_text = " ".join(all_transcripts)
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    print("📝 Full transcript saved to transcript.txt")

    # ✅ (Optional) Generate summary (placeholder here)
    # Replace with GPT/HuggingFace call
    summary = " ".join(full_text.split()[:50]) + "..."  # simple fake summary
    print("\n📌 Summary:\n", summary)
