import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from conscious_core import ConsciousnessEngine
import sys
import pyttsx3
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

class VoiceAIUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{AI_NAME} (by {AI_CREATOR}) - Advanced Voice AI")
        self.engine = ConsciousnessEngine()
        self.listening = False
        self.setup_ui()

    def setup_ui(self):
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', font=("Segoe UI", 12), bg="#181c24", fg="#e0e0e0")
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.mood_label = tk.Label(self.root, text="Mood: Neutral", font=("Segoe UI", 11, "bold"), fg="#00e676", bg="#232946")
        self.mood_label.pack(padx=10, pady=(0,5), fill=tk.X)

        entry_frame = tk.Frame(self.root, bg="#232946")
        entry_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry = tk.Entry(entry_frame, font=("Segoe UI", 12), bg="#232946", fg="#e0e0e0", insertbackground="#e0e0e0")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.entry.bind('<Return>', lambda e: self.send_message())

        self.speak_btn = tk.Button(entry_frame, text="🎤 Speak", font=("Segoe UI", 11, "bold"), command=self.listen_voice, bg="#00bcd4", fg="white", activebackground="#0097a7")
        self.speak_btn.pack(side=tk.LEFT, padx=(0,5))

        self.send_btn = tk.Button(entry_frame, text="Send", font=("Segoe UI", 11, "bold"), command=self.send_message, bg="#00e676", fg="#232946", activebackground="#00c853")
        self.send_btn.pack(side=tk.LEFT)

        self.exit_btn = tk.Button(self.root, text="Exit", font=("Segoe UI", 11), command=self.root.quit, bg="#ff1744", fg="white", activebackground="#b2102f")
        self.exit_btn.pack(pady=(0,10))

        self.animate_mood()

    def update_chat(self, sender, message, mood=None):
        self.chat_area.config(state='normal')
        if sender == 'user':
            self.chat_area.insert(tk.END, f"You: {message}\n", 'user')
        else:
            mood_str = f" [{mood}]" if mood else ""
            self.chat_area.insert(tk.END, f"{AI_NAME}{mood_str}: {message}\n", 'ai')
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def send_message(self):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, tk.END)
        self.update_chat('user', user_input)
        threading.Thread(target=self.process_input, args=(user_input,)).start()

    def listen_voice(self):
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        self.speak_btn.config(text="🎤 Listening...", state='disabled', bg="#ffd600")
        self.root.update()
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            self.update_chat('user', user_input)
            threading.Thread(target=self.process_input, args=(user_input,)).start()
        except Exception as e:
            self.update_chat('ai', f"[Voice Error] {e}")
        finally:
            self.speak_btn.config(text="🎤 Speak", state='normal', bg="#00bcd4")

    def process_input(self, user_input):
        factual_keywords = ["who", "what", "when", "where", "why", "how", "define", "explain", "tell me about"]
        if any(user_input.lower().startswith(k) for k in factual_keywords) and search_engine:
            results = search_engine.search_and_extract(user_input)
            if results and results[0]['content']:
                response = results[0]['content'][:300] + ("..." if len(results[0]['content']) > 300 else "")
                self.update_chat('ai', response, self.engine.get_current_mood())
                self.speak(response)
                self.update_mood_label()
                return
        response = self.engine.respond(user_input)
        self.update_chat('ai', response, self.engine.get_current_mood())
        self.speak(response)
        self.update_mood_label()

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def update_mood_label(self):
        mood = self.engine.get_current_mood().capitalize()
        emoji = {
            'happy': '😊', 'sad': '😔', 'angry': '😠', 'worried': '😟', 'neutral': '🤖'
        }
        mood_icon = emoji.get(mood.lower().split('/')[0], '🤖')
        self.mood_label.config(text=f"Mood: {mood_icon} {mood}")

    def animate_mood(self):
        # Simple animation: flash mood label color
        import itertools
        colors = itertools.cycle(["#00e676", "#ffd600", "#00bcd4", "#ff1744"])
        def flash():
            self.mood_label.config(bg=next(colors))
            self.root.after(800, flash)
        flash()

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#232946")
    app = VoiceAIUI(root)
    root.geometry("600x500")
    root.mainloop()
