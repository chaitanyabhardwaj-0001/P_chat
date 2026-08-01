import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# Initialize client using an environment variable
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>My AI Web App</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { font-family: sans-serif; max-width: 650px; margin: 40px auto; padding: 20px; }
        #chatbox { 
            border: 1px solid #ccc; 
            height: 400px; 
            overflow-y: auto; 
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 8px; 
            background-color: #fdfdfd;
        }
        .message { margin-bottom: 15px; line-height: 1.5; }
        .user-msg { color: #1a73e8; }
        .ai-msg { color: #202124; border-top: 1px solid #eee; padding-top: 8px; }
        .ai-msg ul, .ai-msg ol { padding-left: 20px; margin: 5px 0; }
        .ai-msg p { margin: 5px 0; }
        input { width: 75%; padding: 10px; font-size: 14px; }
        button { padding: 10px 15px; font-size: 14px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>My Custom AI Web App</h2>
    <div id="chatbox"></div>
    <input type="text" id="userInput" placeholder="Ask something..." onkeydown="if(event.key==='Enter') sendMessage()" />
    <button onclick="sendMessage()">Send</button>

    <script>
        let chatHistory = [];

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatbox = document.getElementById('chatbox');
            const text = input.value.trim();
            if (!text) return;

            chatbox.innerHTML += `<div class="message user-msg"><b>You:</b> ${text}</div>`;
            input.value = '';

            chatHistory.push({ role: 'user', parts: [{ text: text }] });

            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: chatHistory })
            });
            const data = await response.json();

            const formattedReply = marked.parse(data.reply);
            chatbox.innerHTML += `<div class="message ai-msg"><b>AI:</b> ${formattedReply}</div>`;

            chatHistory.push({ role: 'model', parts: [{ text: data.reply }] });
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    history = request.json.get('history', [])
    user_prompt = history[-1]['parts'][0]['text'] if history else ""

    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=history[:-1],
        config={
            "system_instruction": (
                "Your name is ByteBot. You are a helpful AI assistant. "
                "Always structure your answers clearly using bold headings, bullet points, "
                "and concise paragraphs."
            )
        }
    )

    response = chat.send_message(user_prompt)
    return jsonify({'reply': response.text})

# Vercel needs the app variable exported directly