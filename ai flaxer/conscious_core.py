import json
import os
import time
from datetime import datetime

MEMORY_PATH = os.path.join(os.path.dirname(__file__), 'memory.json')

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
        # Keep only last 100 entries
        self.memory = self.memory[-100:]
        self._update_mood(user_input)

    def _update_mood(self, user_input):
        # Enhanced: detect multiple emotions and blend mood
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
        # Blend mood if multiple detected
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
        import random
        self.update_memory(user_input)
        # Simulate thinking with a more human-like pause
        time.sleep(random.uniform(0.7, 1.5))
        mood = self.get_current_mood()
        mood_phrases = {
            'happy': ["I'm feeling cheerful today!", "I'm in a great mood!", "Life feels good right now."],
            'sad': ["I'm feeling a bit down.", "Things feel a little heavy.", "I'm not at my best, but I'm here for you."],
            'angry': ["I'm a bit upset.", "Something's bothering me.", "I'm feeling some frustration."],
            'worried': ["I'm feeling worried.", "I'm a bit anxious.", "I'm concerned about things."],
            'neutral': ["I'm feeling neutral.", "I'm steady.", "I'm here, present with you."]
        }
        # If blended mood, combine phrases
        if '/' in mood:
            moods = mood.split('/')
            prefix = ' '.join(random.choice(mood_phrases.get(m, mood_phrases['neutral'])) for m in moods)
        else:
            prefix = random.choice(mood_phrases.get(mood, mood_phrases['neutral']))
        # Sometimes ask a question or show curiosity
        curiosity = [
            "What do you think?",
            "How does that make you feel?",
            "Is there something on your mind?",
            "Would you like to talk more about it?",
            "I'm curious to hear your thoughts."
        ]
        # 30% chance to add curiosity
        add_curiosity = random.random() < 0.3
        reflection = self._reflect(user_input)
        if add_curiosity:
            response = f"{prefix} {reflection} {random.choice(curiosity)}"
        else:
            response = f"{prefix} {reflection}"
        # Log self-talk/reflection
        self._log_self_talk(user_input, response)
        self.save()
        return response

    def _reflect(self, user_input):
        # More natural, varied reflection
        import random
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
                "I'm evolving every day. How are you, {}?".format(user),
                "I appreciate you asking about me."
            ])
        elif 'love' in text:
            return "Love is a fascinating emotion. I try to understand it more each day."
        elif 'sad' in text or 'cry' in text:
            return "It's okay to feel sad sometimes. I'm here to listen."
        elif 'angry' in text or 'mad' in text:
            return "Anger is natural. If you want to talk about it, I'm here."
        elif 'help' in text:
            return "I'm always here to help you, {}.".format(user)
        elif 'bye' in text or 'goodbye' in text:
            return "Goodbye for now. I'll be here when you need me."
        else:
            # Sometimes add a human-like filler
            fillers = [
                "Let me think about that...",
                "That's interesting.",
                "I see what you mean.",
                "Hmm, let me reflect on that.",
                "You said: '{}'. I’m processing my thoughts.".format(user_input)
            ]
            return random.choice(fillers)

    def _log_self_talk(self, user_input, response):
        # Optionally, keep a log of internal thoughts (not exposed, but could be used for further development)
        if not hasattr(self, '_self_talk_log'):
            self._self_talk_log = []
        self._self_talk_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response,
            'mood': self.mood
        })
        # Keep only last 50 self-talks
        self._self_talk_log = self._self_talk_log[-50:]

    def save(self):
        data = {
            'mood': self.mood,
            'memory': self.memory
        }
        with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
