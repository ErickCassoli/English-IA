import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def create_session():
    print("Creating session...")
    resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
    resp.raise_for_status()
    session = resp.json()
    print(f"Session created: {session['session_id']}")
    return session['session_id']

def send_message(session_id, text):
    print(f"Sending: '{text}'...")
    start = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/chat/{session_id}/message", json={"text": text}, timeout=120)
        resp.raise_for_status()
        duration = time.time() - start
        print(f"Received ({duration:.2f}s): {resp.json()['reply'][:50]}...")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    try:
        sid = create_session()
        send_message(sid, "Hello")
        
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        send_message(sid, "My week is boring")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
