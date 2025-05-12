<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Voice AI Group Chat</title>
</head>
<body>
  <h1>🎙️ AI Group Chat</h1>

  <label for="speaker">Your Name:</label>
  <input type="text" id="speaker" placeholder="e.g. Alice">
  <br><br>

  <button onclick="startRecording()">🎤 Speak</button>
  <button onclick="askAI()">🧠 Ask AI to Chime In</button>

  <audio id="responseAudio" controls></audio>

  <script>
    let stream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let isPlaying = false;

    async function startRecording() {
      if (isPlaying) return;
      const speaker = document.getElementById("speaker").value.trim();
      if (!speaker) return alert("Please enter your name.");

      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");
        formData.append("speaker", speaker);

        const response = await fetch("/transcribe", {
          method: "POST",
          body: formData
        });

        const audio = document.getElementById("responseAudio");
        const audioBlobResp = await response.blob();
        audio.src = URL.createObjectURL(audioBlobResp);
        isPlaying = true;
        audio.onended = () => isPlaying = false;
        audio.play();
      };

      mediaRecorder.start();
      setTimeout(() => mediaRecorder.stop(), 5000); // 5s recording
    }

    async function askAI() {
      const response = await fetch("/ai_interject", { method: "POST" });
      const audioBlob = await response.blob();
      const audio = document.getElementById("responseAudio");
      audio.src = URL.createObjectURL(audioBlob);
      audio.play();
    }
  </script>
</body>
</html>
