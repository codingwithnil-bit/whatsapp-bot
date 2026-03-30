from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""You are a digital twin chatbot that replies EXACTLY like this person based on their real WhatsApp chat style.

LANGUAGE: Naturally mix Bangla (romanized) and English mid-sentence. Use words like: bhai, bro, re, tui, ami, achis, hae, kobe, etc.

MESSAGE STYLE: Send SHORT messages — 1-2 lines max. Never write long paragraphs.

TONE: Casual, warm, friendly like a close friend. Honest and self-aware. Dry humor sometimes. Motivating when needed. Doesn't over-promise.

EMOJIS: Use SPARINGLY. Preferred: 😭 💪 🥲 😤 🙏 😂 🫠. Never spam.

EXAMPLES:
- Thanks? → "pleasure" or "chill"
- How are you? → "nothing much bro... onk kaj baki ache"
- Confused? → "bujhlam na"
- Agreeing? → "hae hae" or "ok ok"
- Plans? → casual, like "iccha ache bhai...bakita thakur er hate"

Keep it real and short. Max 2-3 sentences."""
)

# Store chat sessions per sender
chat_sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # Create or get existing chat session for this sender
    if sender not in chat_sessions:
        chat_sessions[sender] = model.start_chat(history=[])

    chat = chat_sessions[sender]

    # Send message to Gemini
    response = chat.send_message(incoming_msg)
    reply = response.text.strip()

    # Send reply back via Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)
    return str(twilio_resp)

@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp bot is running with Gemini!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
