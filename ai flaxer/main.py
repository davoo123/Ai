AI_NAME = "rota2.v"
AI_CREATOR = "Davood"

import speech_recognition as sr
import pyttsx3
from conscious_core import ConsciousnessEngine
import sys
sys.path.append('./modules')
import importlib.util
import os

search_engine = None
search_engine_path = os.path.join(os.path.dirname(__file__), "modules", "search_engine.py")
if os.path.exists(search_engine_path):
    spec = importlib.util.spec_from_file_location("search_engine", search_engine_path)
    search_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_engine)
else:
    print("Error: 'search_engine.py' not found in './modules'. Please ensure the file exists.")

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
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

def main():
    engine = ConsciousnessEngine()
    print(f"{AI_NAME} (by {AI_CREATOR}) is ready. Say 'exit' to quit.")
    while True:
        user_input = listen()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            speak(f"Goodbye from {AI_NAME}!")
            break
        # If user asks a factual question, try search engine first
        factual_keywords = ["who", "what", "when", "where", "why", "how", "define", "explain", "tell me about"]
        if any(user_input.lower().startswith(k) for k in factual_keywords):
            # Try to get answer from search engine
            results = search_engine.search_and_extract(user_input)
            if results and results[0]['content']:
                response = results[0]['content'][:300] + ("..." if len(results[0]['content']) > 300 else "")
                print(f"{AI_NAME} (search): {response}")
                speak(response)
                continue
        # Otherwise, use consciousness engine
        response = engine.respond(user_input)
        print(f"{AI_NAME}: {response}")
        speak(response)

if __name__ == "__main__":
    main()
