from flask import Flask, request, jsonify, send_file, render_template
import openai
import requests
import os
from io import BytesIO

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    audio_file = request.files["audio"]
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": transcript["text"]}]
    )
    reply_text = response["choices"][0]["message"]["content"]

    # Send to ElevenLabs
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    voice_id = "Rachel"  # You can change this to another voice ID
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    tts_response = requests.post(tts_url, headers=headers, json={
        "text": reply_text,
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    })

    return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)
