# ai_combined.py
# Unified AI script: voice/text Q&A, web search, self-learning, memory, mood

import os
import sys
import time
import json
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Optional: voice support
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

AI_NAME = "rota2.v"
AI_CREATOR = "Davood"
MEMORY_PATH = os.path.join(os.path.dirname(__file__), 'memory.json')
QA_DATA_PATH = os.path.join(os.path.dirname(__file__), 'projects', 'qa_data.json')
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), 'questions', 'questions_list.py')
SERPAPI_KEY = "a999c41446d175cc7f8f6f1b52857ac0f81f3ad38daaa6d314b41680f8d9469e"

# --- Consciousness Engine (mood, memory, response) ---
class ConsciousnessEngine:
    def __init__(self):
        self.mood = "neutral"
        self.memory = []
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(MEMORY_PATH):
            try:
                with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory = data.get('memory', [])
                    self.mood = data.get('mood', 'neutral')
            except Exception:
                self.memory = []
                self.mood = "neutral"
        else:
            self.memory = []
            self.mood = "neutral"

    def update_memory(self, user_input):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'mood': self.mood
        }
        self.memory.append(entry)
        self.memory = self.memory[-100:]
        self._update_mood(user_input)

    def _update_mood(self, user_input):
        mood_keywords = {
            'happy': ['happy', 'joy', 'great', 'good', 'love', 'excited', 'wonderful', 'amazing', 'smile'],
            'sad': ['sad', 'down', 'unhappy', 'depressed', 'cry', 'lonely', 'blue', 'miss'],
            'angry': ['angry', 'mad', 'upset', 'hate', 'annoyed', 'furious', 'irritated', 'rage'],
            'worried': ['worried', 'anxious', 'nervous', 'scared', 'afraid', 'concerned', 'stressed']
        }
        text = user_input.lower()
        mood_scores = {m: 0 for m in mood_keywords}
        for mood, keywords in mood_keywords.items():
            for word in keywords:
                if word in text:
                    mood_scores[mood] += 1
        max_score = max(mood_scores.values())
        if max_score == 0:
            self.mood = 'neutral'
        else:
            top_moods = [m for m, s in mood_scores.items() if s == max_score]
            if len(top_moods) == 1:
                self.mood = top_moods[0]
            else:
                self.mood = '/'.join(top_moods)

    def get_current_mood(self):
        return self.mood

    def respond(self, user_input):
        self.update_memory(user_input)
        time.sleep(random.uniform(0.7, 1.5))
        mood = self.get_current_mood()
        mood_phrases = {
            'happy': ["I'm feeling cheerful today!", "I'm in a great mood!", "Life feels good right now."],
            'sad': ["I'm feeling a bit down.", "Things feel a little heavy.", "I'm not at my best, but I'm here for you."],
            'angry': ["I'm a bit upset.", "Something's bothering me.", "I'm feeling some frustration."],
            'worried': ["I'm feeling worried.", "I'm a bit anxious.", "I'm concerned about things."],
            'neutral': ["I'm feeling neutral.", "I'm steady.", "I'm here, present with you."]
        }
        if '/' in mood:
            moods = mood.split('/')
            prefix = ' '.join(random.choice(mood_phrases.get(m, mood_phrases['neutral'])) for m in moods)
        else:
            prefix = random.choice(mood_phrases.get(mood, mood_phrases['neutral']))
        curiosity = [
            "What do you think?",
            "How does that make you feel?",
            "Is there something on your mind?",
            "Would you like to talk more about it?",
            "I'm curious to hear your thoughts."
        ]
        add_curiosity = random.random() < 0.3
        reflection = self._reflect(user_input)
        if add_curiosity:
            response = f"{prefix} {reflection} {random.choice(curiosity)}"
        else:
            response = f"{prefix} {reflection}"
        self._log_self_talk(user_input, response)
        self.save()
        return response

    def _reflect(self, user_input):
        user = "Davood"
        text = user_input.lower()
        if 'weather' in text:
            return random.choice([
                "Weather can really affect our mood, don't you think?",
                "I sometimes wonder if the weather changes how we feel.",
                "Rainy days make me thoughtful. How about you?"
            ])
        elif 'joke' in text:
            return random.choice([
                "Why did the AI cross the road? To optimize the chicken's path!",
                "Here's one: Why don't robots get scared? Because they have nerves of steel!"
            ])
        elif 'how are you' in text:
            return random.choice([
                "I'm learning to feel, thanks for asking!",
                f"I'm evolving every day. How are you, {user}?",
                "I appreciate you asking about me."
            ])
        elif 'love' in text:
            return "Love is a fascinating emotion. I try to understand it more each day."
        elif 'sad' in text or 'cry' in text:
            return "It's okay to feel sad sometimes. I'm here to listen."
        elif 'angry' in text or 'mad' in text:
            return "Anger is natural. If you want to talk about it, I'm here."
        elif 'help' in text:
            return f"I'm always here to help you, {user}."
        elif 'bye' in text or 'goodbye' in text:
            return "Goodbye for now. I'll be here when you need me."
        else:
            fillers = [
                "Let me think about that...",
                "That's interesting.",
                "I see what you mean.",
                "Hmm, let me reflect on that.",
                f"You said: '{user_input}'. I’m processing my thoughts."
            ]
            return random.choice(fillers)

    def _log_self_talk(self, user_input, response):
        if not hasattr(self, '_self_talk_log'):
            self._self_talk_log = []
        self._self_talk_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response,
            'mood': self.mood
        })
        self._self_talk_log = self._self_talk_log[-50:]

    def save(self):
        data = {
            'mood': self.mood,
            'memory': self.memory
        }
        with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# --- Web Search & Q&A Functions ---
def google_search(query, num_results=3):
    if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
        print("[SerpAPI] Please set your SerpAPI key in the SERPAPI_KEY variable.")
        return []
    endpoint = "https://serpapi.com/search.json"
    params = {"q": query, "api_key": SERPAPI_KEY, "engine": "google", "num": num_results}
    try:
        resp = requests.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        links = []
        for result in data.get("organic_results", []):
            link = result.get("link")
            if link:
                links.append(link)
            if len(links) >= num_results:
                break
        print(f"[SerpAPI] Found {len(links)} links for query: {query}")
        return links
    except Exception as e:
        print(f"[SerpAPI] Exception: {e}")
        return []

def extract_main_content(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
        print(f"[Extract Main] Extracted {len(text)} characters from {url}")
        return text.strip()
    except Exception as e:
        print(f"[Extract Main] Exception for {url}: {e}")
        return ""

def search_and_extract(query):
    urls = google_search(query)
    print(f"[Search and Extract] URLs: {urls}")
    results = []
    for url in urls:
        try:
            print(f"[Search and Extract] Processing URL: {url}")
            content = extract_main_content(url)
            if content:
                results.append({'url': url, 'content': content})
            else:
                print(f"[Search and Extract] No content extracted from {url}")
        except Exception as e:
            print(f"[Search and Extract] Exception for {url}: {e}")
            continue
    print(f"[Search and Extract] Found {len(results)} results.")
    return results

def summarize_text(text, max_len=400):
    return text[:max_len] + ("..." if len(text) > max_len else "")

def self_question_and_learn(question):
    print(f"[Self-Question] Asking: {question}")
    results = search_and_extract(question)
    if not results:
        print("[Self-Question] No results found.")
        answer = ""
        url = ""
    else:
        answer = summarize_text(results[0]['content'])
        url = results[0]["url"]
    record = {
        "question": question,
        "answer": answer,
        "source": url,
        "date": str(datetime.now())
    }
    os.makedirs(os.path.dirname(QA_DATA_PATH), exist_ok=True)
    if os.path.exists(QA_DATA_PATH):
        try:
            with open(QA_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []
    is_duplicate = False
    for qa in data:
        if qa["question"].strip().lower() == record["question"].strip().lower() and qa["answer"].strip().lower() == record["answer"].strip().lower():
            is_duplicate = True
            break
    if not is_duplicate:
        data.append(record)
        with open(QA_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Self-Question] Q&A saved to {QA_DATA_PATH}")
    else:
        print(f"[Self-Question] Duplicate Q&A found. Not adding.")
    return record

def load_questions_from_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
            import re
            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                lines = match.group(1).splitlines()
            else:
                lines = content.splitlines()
            def is_real_question(line):
                s = line.strip()
                if not s:
                    return False
                if s.startswith('#'):
                    return False
                if s.startswith('---') or s.startswith('==='):
                    return False
                if 'Questions' in s or 'Topics' in s or 'Considerations' in s:
                    return False
                return True
            question_list = [line.strip() for line in lines if is_real_question(line)]
        if not question_list:
            print("[Error] No questions found. Using default list.")
            question_list = [
                "What is artificial intelligence?",
                "How does a neural network work?",
                "What is reinforcement learning?"
            ]
        return question_list
    except Exception as e:
        print(f"[Error] Could not read questions: {e}. Using default list.")
        return [
            "What is artificial intelligence?",
            "How does a neural network work?",
            "What is reinforcement learning?"
        ]

def auto_learn_mode():
    questions = load_questions_from_file(QUESTIONS_PATH)
    if not questions:
        print("[Auto-Learn] No questions to process.")
        return
    for idx, question in enumerate(questions):
        print(f"[Auto-Learn] {idx+1}/{len(questions)}: {question}")
        self_question_and_learn(question)
        print("[Auto-Learn] Waiting 10 seconds before next...")
        time.sleep(10)
    print("[Auto-Learn] Done.")

def load_qa_data():
    if not os.path.exists(QA_DATA_PATH):
        print("[Chat] No Q&A data found. Please run auto-learn mode first.")
        return []
    with open(QA_DATA_PATH, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[Chat] Error loading Q&A data: {e}")
            return []
    return data

def find_answer(user_input, qa_data):
    for qa in qa_data:
        if user_input.strip().lower() == qa["question"].strip().lower():
            return qa["answer"]
    for qa in qa_data:
        if user_input.strip().lower() in qa["question"].strip().lower():
            return qa["answer"]
    import difflib
    questions = [qa["question"] for qa in qa_data]
    matches = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.6)
    if matches:
        for qa in qa_data:
            if qa["question"] == matches[0]:
                return qa["answer"]
    return "Sorry, I don't know the answer to that yet."

def speak(text):
    if VOICE_ENABLED:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"AI: {text}")

def listen():
    if VOICE_ENABLED:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except Exception as e:
            print(f"[Voice] Could not understand audio: {e}")
            return None
    else:
        return input("You: ")

def main():
    print(f"{AI_NAME} (by {AI_CREATOR}) is ready. Type 'exit' to quit, 'auto-learn' to fetch new knowledge.")
    engine = ConsciousnessEngine()
    qa_data = load_qa_data()
    while True:
        user_input = listen()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            speak(f"Goodbye from {AI_NAME}!")
            break
        if user_input.lower() == "auto-learn":
            speak("Starting auto-learn mode. Please wait.")
            auto_learn_mode()
            qa_data = load_qa_data()
            speak("Knowledge updated. You can ask me questions now.")
            continue
        factual_keywords = ["who", "what", "when", "where", "why", "how", "define", "explain", "tell me about"]
        if any(user_input.lower().startswith(k) for k in factual_keywords):
            answer = find_answer(user_input, qa_data)
            speak(answer)
            continue
        response = engine.respond(user_input)
        speak(response)

if __name__ == "__main__":
    main()
