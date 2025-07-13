import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

# For SerpAPI (Google Search)
SERPAPI_KEY = "a999c41446d175cc7f8f6f1b52857ac0f81f3ad38daaa6d314b41680f8d9469e"  # <-- Your SerpAPI key

def google_search(query, num_results=3):
    """Perform a web search using SerpAPI (Google Search) and return top result URLs."""
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
    """Extract main text content from a web page, filtering out menus/ads."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove scripts/styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        # Get text from main content
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
        print(f"[Extract Main] Extracted {len(text)} characters from {url}")
        return text.strip()
    except Exception as e:
        print(f"[Extract Main] Exception for {url}: {e}")
        return ""

def search_and_extract(query):
    """Search and extract clean text from top results."""
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

def fetch_google_news(query, num_results=5):
    """Fetch news article URLs from Google News search."""
    search_url = f"https://news.google.com/search?q={query}"
    try:
        resp = requests.get(search_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all('a', attrs={'href': True}):
            href = a['href']
            if href.startswith('./articles/'):
                url = "https://news.google.com" + href[1:]
                if url not in links:
                    links.append(url)
            if len(links) >= num_results:
                break
        print(f"[Google News] Found {len(links)} news links for query: {query}")
        return links
    except Exception as e:
        print(f"[Google News] Exception: {e}")
        return []

def extract_news_article(url):
    """Extract main content from a Google News article (follows redirect)."""
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove scripts/styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
        print(f"[Extract News] Extracted {len(text)} characters from {url}")
        return text.strip()
    except Exception as e:
        print(f"[Extract News] Exception for {url}: {e}")
        return ""

def self_learn_from_news(query="AI technology", interval=3600):
    """
    Periodically fetch news, extract content, and yield results for self-learning.
    To be called in a loop or scheduled task.
    """
    while True:
        print(f"[Self-Learning] Fetching news for: {query}")
        news_urls = fetch_google_news(query)
        print(f"[Self-Learning] News URLs: {news_urls}")
        for url in news_urls:
            print(f"[Self-Learning] Processing news URL: {url}")
            content = extract_news_article(url)
            if content:
                print(f"[Self-Learning] Yielding content from {url}")
                yield {'url': url, 'content': content}
            else:
                print(f"[Self-Learning] No content extracted from {url}")
        print(f"[Self-Learning] Sleeping for {interval} seconds...")
        time.sleep(interval)

def summarize_text(text, max_len=400):
    """Simple summarizer: returns the first max_len characters."""
    return text[:max_len] + ("..." if len(text) > max_len else "")

def self_question_and_learn(question, projects_dir="../projects/"):
    """
    Ask a question, search for the answer, and save Q&A as a code comment in a .py file.
    """
    print(f"[Self-Question] Asking: {question}")
    results = search_and_extract(question)
    if not results:
        print("[Self-Question] No results found.")
        answer = ""
        url = ""
    else:
        answer = summarize_text(results[0]['content'])
        url = results[0]["url"]
    # Prepare JSON record
    record = {
        "question": question,
        "answer": answer,
        "source": url,
        "date": str(datetime.now())
    }
    # Always use absolute path for projects_dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_projects_dir = os.path.abspath(os.path.join(base_dir, '..', 'projects'))
    os.makedirs(abs_projects_dir, exist_ok=True)
    json_path = os.path.join(abs_projects_dir, "qa_data.json")
    import json
    # Read existing data
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []
    # Check for duplicate (same question and answer)
    is_duplicate = False
    for qa in data:
        if qa["question"].strip().lower() == record["question"].strip().lower() and qa["answer"].strip().lower() == record["answer"].strip().lower():
            is_duplicate = True
            break
    if not is_duplicate:
        data.append(record)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Self-Question] Q&A saved to {json_path}")
        # Deduplicate after adding
        try:
            deduplicate_qa_data()
        except Exception as e:
            print(f"[Self-Question] Deduplication error: {e}")
    else:
        print(f"[Self-Question] Duplicate Q&A found. Not adding.")
    return record


def continuous_question_loop(questions, interval=10, projects_dir="../projects/"):
    """
    Continuously ask a list of questions, fetch answers from the network, and save Q&A.
    If a question is a function, it will be called to get the next question (for dynamic questioning).
    """
    import types
    idx = 0
    while True:
        if isinstance(questions, types.GeneratorType):
            try:
                question = next(questions)
            except StopIteration:
                print("[Loop] No more questions in generator.")
                break
        elif callable(questions):
            question = questions()
        elif isinstance(questions, list):
            if idx >= len(questions):
                print("[Loop] All questions processed. Restarting from beginning.")
                idx = 0
            question = questions[idx]
            idx += 1
        else:
            print("[Loop] Invalid questions input.")
            break
        print(f"[Loop] Asking: {question}")
        result = self_question_and_learn(question, projects_dir=projects_dir)
        if result:
            print(f"[Loop] Answered: {result['answer'][:100]}...")
        else:
            print("[Loop] No answer found.")
        print(f"[Loop] Waiting {interval} seconds before next question...")
        time.sleep(interval)


# --- New function for automatic question answering from a list ---
def auto_question_answer_loop(question_list, interval=10, projects_dir="../projects/"):
    """
    Automatically processes a list of questions one by one:
    - For each question, fetches the answer from the internet and saves it.
    - Moves to the next question after the previous one is answered.
    - Stops when all questions are answered.
    """
    for idx, question in enumerate(question_list):
        print(f"[AutoQA] Question {idx+1}/{len(question_list)}: {question}")
        result = self_question_and_learn(question, projects_dir=projects_dir)
        if result:
            print(f"[AutoQA] Answered: {result['answer'][:100]}...")
        else:
            print(f"[AutoQA] No answer found for: {question}")
        if idx < len(question_list) - 1:
            print(f"[AutoQA] Waiting {interval} seconds before next question...")
            time.sleep(interval)
    print("[AutoQA] All questions processed.")


# Example usage in main
if __name__ == "__main__":
    # --- Q&A Deduplication Function ---
    def deduplicate_qa_data():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qa_path = os.path.abspath(os.path.join(base_dir, '..', 'projects', 'qa_data.json'))
        if not os.path.exists(qa_path):
            print("[Dedup] No Q&A data found.")
            return
        import json
        with open(qa_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[Dedup] Error loading Q&A data: {e}")
                return
        seen = set()
        deduped = []
        for qa in data:
            key = (qa["question"].strip().lower(), qa["answer"].strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append(qa)
        if len(deduped) < len(data):
            with open(qa_path, "w", encoding="utf-8") as f:
                json.dump(deduped, f, ensure_ascii=False, indent=2)
            print(f"[Dedup] Removed {len(data) - len(deduped)} duplicate Q&A pairs.")
        else:
            print("[Dedup] No duplicates found.")

    # Read questions from questions/questions_list.py as plain text (one per line)
    import os
    questions_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../questions/questions_list.py'))
    question_list = []
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
                # Only keep lines that are not empty, not comments, and not section headers
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
                print("[Error] No questions found in questions/questions_list.py. Using default list.")
                question_list = [
                    "What is artificial intelligence?",
                    "How does a neural network work?",
                    "What is reinforcement learning?"
                ]
            return question_list
        except Exception as e:
            print(f"[Error] Could not read questions/questions_list.py: {e}. Using default list.")
            return [
                "What is artificial intelligence?",
                "How does a neural network work?",
                "What is reinforcement learning?"
            ]

    def run_auto_qa():
        question_list = load_questions_from_file(questions_path)
        # Load existing Q&A data for deduplication
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qa_path = os.path.abspath(os.path.join(base_dir, '..', 'projects', 'qa_data.json'))
        existing_qs = set()
        if os.path.exists(qa_path):
            import json
            with open(qa_path, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for qa in data:
                        existing_qs.add(qa["question"].strip().lower())
                except Exception:
                    pass
        # Only ask questions not already answered
        filtered_questions = [q for q in question_list if q.strip().lower() not in existing_qs]
        if not filtered_questions:
            print("[AutoQA] All questions already have answers. Nothing to do.")
            return
        auto_question_answer_loop(filtered_questions, interval=20)
        deduplicate_qa_data()

    import json
    def load_qa_data():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qa_path = os.path.abspath(os.path.join(base_dir, '..', 'projects', 'qa_data.json'))
        if not os.path.exists(qa_path):
            print("[Chat] No Q&A data found. Please run the auto-question-answer loop first.")
            return []
        with open(qa_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[Chat] Error loading Q&A data: {e}")
                return []
        return data

    def find_answer(user_input, qa_data):
        # Simple match: exact or case-insensitive
        for qa in qa_data:
            if user_input.strip().lower() == qa["question"].strip().lower():
                return qa["answer"]
        # Try partial match
        for qa in qa_data:
            if user_input.strip().lower() in qa["question"].strip().lower():
                return qa["answer"]
        # Fuzzy match using difflib
        import difflib
        questions = [qa["question"] for qa in qa_data]
        matches = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.6)
        if matches:
            for qa in qa_data:
                if qa["question"] == matches[0]:
                    return qa["answer"]
        return "Sorry, I don't know the answer to that yet."

    print("\n[AI Chat] Say your question (or say 'exit' to quit, or say 'get the data' to update knowledge):")
    qa_data = load_qa_data()
    import speech_recognition as sr
    import pyttsx3
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    tts_engine = pyttsx3.init()
    def speak(text):
        tts_engine.say(text)
        tts_engine.runAndWait()
    while True:
        print("Listening...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
        except Exception as e:
            print(f"[Voice] Could not understand audio: {e}")
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            speak("Goodbye!")
            print("AI: Goodbye!")
            break
        if user_input.lower() == "get the data":
            speak("Updating my knowledge. Please wait.")
            print("[AI] Fetching new answers from the web...")
            run_auto_qa()
            qa_data = load_qa_data()
            speak("Knowledge updated. You can ask me questions now.")
            continue
        if not user_input:
            continue
        answer = find_answer(user_input, qa_data)
        print(f"AI: {answer}\n")
        speak(answer)
