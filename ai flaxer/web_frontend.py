from flask import Flask, request, jsonify, render_template_string
from conscious_core import ConsciousnessEngine
import importlib.util
import os

AI_NAME = "rota2.v"
AI_CREATOR = "Davood"

# Dynamically load search_engine
search_engine = None
search_engine_path = os.path.join(os.path.dirname(__file__), "modules", "search_engine.py")
if os.path.exists(search_engine_path):
    spec = importlib.util.spec_from_file_location("search_engine", search_engine_path)
    search_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_engine)

app = Flask(__name__)
engine = ConsciousnessEngine()

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ ai_name }} (by {{ ai_creator }})</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #232946; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; }
        #chat { width: 100%; max-width: 600px; margin: 30px auto; background: #181c24; border-radius: 10px; padding: 20px; box-shadow: 0 0 20px #0004; }
        .msg { margin: 10px 0; }
        .user { color: #ffd600; }
        .ai { color: #00e676; }
        #mood { font-weight: bold; margin-bottom: 10px; }
        #input-area { display: flex; gap: 8px; margin-top: 15px; }
        #input { flex: 1; padding: 8px; border-radius: 5px; border: none; background: #232946; color: #e0e0e0; }
        #send { background: #00e676; color: #232946; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; cursor: pointer; }
        #send:hover { background: #00bcd4; color: #fff; }
        .bubble { padding: 10px; border-radius: 8px; margin-bottom: 5px; display: inline-block; max-width: 80%; }
        .bubble.user { background: #2d3250; }
        .bubble.ai { background: #263238; }
        @keyframes moodFlash { 0%{color:#00e676;} 50%{color:#ffd600;} 100%{color:#00e676;} }
        #mood { animation: moodFlash 2s infinite; }
    </style>
</head>
<body>
    <div id="chat">
        <h2>{{ ai_name }} <span style="font-size:0.7em;">(by {{ ai_creator }})</span></h2>
        <div id="mood">Mood: <span id="mood-emoji">🤖</span> <span id="mood-text">Neutral</span></div>
        <div id="messages"></div>
        <div id="input-area">
            <input id="input" type="text" placeholder="Type your message..." autofocus autocomplete="off" />
            <button id="send">Send</button>
        </div>
    </div>
    <script>
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        const messages = document.getElementById('messages');
        const moodText = document.getElementById('mood-text');
        const moodEmoji = document.getElementById('mood-emoji');
        function addMsg(sender, text, mood) {
            let div = document.createElement('div');
            div.className = 'msg';
            let bubble = document.createElement('span');
            bubble.className = 'bubble ' + sender;
            bubble.innerText = text;
            div.appendChild(bubble);
            if (sender === 'ai' && mood) {
                let m = document.createElement('span');
                m.style.marginLeft = '8px';
                m.innerText = `[${mood}]`;
                div.appendChild(m);
            }
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        function updateMood(mood) {
            let emoji = { happy:'😊', sad:'😔', angry:'😠', worried:'😟', neutral:'🤖' };
            let m = (mood||'neutral').toLowerCase().split('/')[0];
            moodText.innerText = mood.charAt(0).toUpperCase() + mood.slice(1);
            moodEmoji.innerText = emoji[m] || '🤖';
        }
        send.onclick = sendMsg;
        input.onkeydown = e => { if(e.key==='Enter') sendMsg(); };
        function sendMsg() {
            let val = input.value.trim();
            if (!val) return;
            addMsg('user', val);
            input.value = '';
            fetch('/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:val})})
            .then(r=>r.json()).then(d=>{
                addMsg('ai', d.response, d.mood);
                updateMood(d.mood);
            });
        }
        // Initial mood
        fetch('/mood').then(r=>r.json()).then(d=>updateMood(d.mood));
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML, ai_name=AI_NAME, ai_creator=AI_CREATOR)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    factual_keywords = ["who", "what", "when", "where", "why", "how", "define", "explain", "tell me about"]
    if any(user_input.lower().startswith(k) for k in factual_keywords) and search_engine:
        results = search_engine.search_and_extract(user_input)
        if results and results[0]['content']:
            response = results[0]['content'][:300] + ("..." if len(results[0]['content']) > 300 else "")
            return jsonify({"response": response, "mood": engine.get_current_mood()})
    response = engine.respond(user_input)
    return jsonify({"response": response, "mood": engine.get_current_mood()})

@app.route("/mood")
def mood():
    return jsonify({"mood": engine.get_current_mood()})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
