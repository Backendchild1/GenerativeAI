import os
import sounddevice as sd
import numpy as np
import threading
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
all_transcripts = []
audio_frames = []
# Load API key from .env
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Create a websocket connection
dg_connection = deepgram.listen.websocket.v("1")

# Transcription callback
def on_message(self, result, **kwargs):
    sentence = result.channel.alternatives[0].transcript
    if sentence:
        print("Transcript:", sentence)

# Attach callback
dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

# Configure transcription
options = LiveOptions(
    model="nova-3",
    language="en",
    encoding="linear16",
    sample_rate=16000,
)

# Start connection
if dg_connection.start(options) is False:
    print(" Failed to start connection")
    exit(1)

# Microphone stream, sending audio to Deepgram
def mic_stream():
    with sd.InputStream(samplerate=16000, channels=1, dtype="int16") as stream:
        print(" Speak into your mic (press Ctrl+C to stop)...")
        while True:
            data, _ = stream.read(1024)  
            audio_bytes = data.tobytes()
            dg_connection.send(audio_bytes)

# Run microphone streaming in a thread
try:
    t = threading.Thread(target=mic_stream)
    t.start()
    t.join()
except KeyboardInterrupt:
    print("Stopping...")
    dg_connection.finish()

   # with wave.open("output.wav", "wb") as  wf:
    #    wf.setchannels(1)
     #   wf.setsampwidth(2)
      #  wf.setframerate(1600)
       # wf.writeframes(b"".join(audio_frames))
