from flask import Flask, request, jsonify, send_file, render_template
import openai
import requests
import os
from io import BytesIO

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# 🔹 Persistent conversation history (global for now)
chat_history = [
    {"role": "system", "content": "You are a helpful assistant. Always respond in English, no matter what language the user speaks."}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        print("🔹 Received audio file")
        audio_file = request.files["audio"]
        audio_bytes = audio_file.read()

        temp_path = "temp_audio.webm"
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)
        print("🔹 Saved temp_audio.webm")

        # 🔹 Transcribe with Whisper
        with open(temp_path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
        user_input = transcript["text"]
        print(f"🔹 Transcription: {user_input}")

        # 🔹 Update chat history and send to GPT
        chat_history.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history
        )

        reply_text = response["choices"][0]["message"]["content"]
        print(f"🔹 ChatGPT replied: {reply_text}")

        # 🔹 Add assistant's response to chat history
        chat_history.append({"role": "assistant", "content": reply_text})

        # 🔹 Optional: trim history to avoid token overflow
        if len(chat_history) > 20:
            chat_history[:] = [chat_history[0]] + chat_history[-18:]  # keep system + 9 rounds

        # 🔹 Send to ElevenLabs
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }

        voice_id = "IKne3meq5aSn9XLyUdCD"  # Your selected ElevenLabs voice
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        tts_response = requests.post(tts_url, headers=headers, json={
            "text": reply_text,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        })

        if tts_response.status_code != 200:
            print(f"❌ ElevenLabs error: {tts_response.text}")
            return "Failed to generate voice", 500

        print("✅ ElevenLabs voice generated!")
        return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
