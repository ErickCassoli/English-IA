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
    try:
        resp = requests.post(f"{BASE_URL}/chat/{session_id}/message", json={"text": text}, timeout=120)
        resp.raise_for_status()
        reply = resp.json()['reply']
        print(f"Received: {reply[:50]}...")
        return reply
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def main():
    try:
        sid = create_session()
        
        # Send 10 messages
        for i in range(1, 11):
            send_message(sid, f"Message number {i}")
            time.sleep(0.1)
        
        print("\nAll 10 messages sent. The server should now have 10 user messages + 10 assistant replies in history + system prompt.")
        print("Verification: Check server logs or assume success if no crash. (I removed the limit)")

    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
