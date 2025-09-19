const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const transcriptDiv = document.getElementById("transcript");

let socket;
let mediaStream;
let audioContext;
let processor;

const DEEPGRAM_API_KEY = "bc9716f4521694e15b25053233f96f41ee1b28a5"; 
startBtn.addEventListener("click", async () => {
  socket = new WebSocket("wss://api.deepgram.com/v1/listen", [
    "token",
    DEEPGRAM_API_KEY,
  ]);

  socket.onopen = async () => {
    console.log("Connected to Deepgram");
    transcriptDiv.textContent = "Listening...";

    // Get microphone
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(mediaStream);

    processor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
      if (socket.readyState === WebSocket.OPEN) {
        const inputData = e.inputBuffer.getChannelData(0);
        const int16Data = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          int16Data[i] = inputData[i] * 0x7fff;
        }
        socket.send(int16Data.buffer);
      }
    };
  };

  socket.onmessage = (message) => {
    const data = JSON.parse(message.data);
    if (data.channel?.alternatives[0]?.transcript) {
      transcriptDiv.textContent = data.channel.alternatives[0].transcript;
    }
  };

  startBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  if (processor) processor.disconnect();
  if (audioContext) audioContext.close();
  if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
  if (socket) socket.close();

  transcriptDiv.textContent += "\n[Stopped]";
  startBtn.disabled = false;
  stopBtn.disabled = true;
});
