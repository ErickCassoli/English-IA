import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def main():
    try:
        # 1. Create Session
        print("Creating session...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        resp.raise_for_status()
        session = resp.json()
        sid = session['session_id']
        print(f"Session: {sid}")

        # 2. Chat with specific context
        context_msg = "I absolutely love eating ice cream especially when it is snowing outside."
        print(f"Sending context: '{context_msg}'")
        resp = requests.post(f"{BASE_URL}/chat/{sid}/message", json={"text": context_msg})
        resp.raise_for_status()
        print(f"AI Reply: {resp.json()['reply'][:50]}...")

        # 3. Finish Session
        print("Finishing session (generating quiz)...")
        # Increase timeout because LLM generation takes time
        resp = requests.post(f"{BASE_URL}/sessions/{sid}/finish", timeout=120)
        resp.raise_for_status()
        data = resp.json()

        # 4. Verify Quiz Content
        print("\n--- Generated Quizzes ---")
        found_context = False
        for q in data.get('quizzes', []):
            print(f"Q: {q['prompt']}")
            print(f"   A: {q['answer']}")
            # Check for keywords
            if "ice cream" in q['prompt'].lower() or "snow" in q['prompt'].lower():
                found_context = True
        
        print(f"\nContext found in quiz? {found_context}")
        
        # 5. Verify Flashcards
        print(f"\nFlashcards Created: {data.get('flashcards_created', 0)}")
        if data.get('flashcards_created', 0) > 0:
            print("SUCCESS: Flashcards were created.")
        else:
            print("WARNING: No flashcards created (maybe no errors detected?)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
