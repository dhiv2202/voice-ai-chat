<!DOCTYPE html>
<html>
<head>
  <title>Voice AI Chat</title>
</head>
<body>
  <h1>Talk to the AI</h1>
  <button onclick="startRecording()">🎙️ Speak</button>
  <audio id="responseAudio" controls></audio>

  <script>
    let mediaRecorder;
    let audioChunks = [];

    async function startRecording() {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");

        const response = await fetch("/transcribe", {
          method: "POST",
          body: formData
        });

        const audio = document.getElementById("responseAudio");
        const audioBlobResp = await response.blob();
        audio.src = URL.createObjectURL(audioBlobResp);
        audio.play();
        audioChunks = [];
      };
      mediaRecorder.start();
      setTimeout(() => mediaRecorder.stop(), 5000); // record for 5 seconds
    }
  </script>
</body>
</html>
