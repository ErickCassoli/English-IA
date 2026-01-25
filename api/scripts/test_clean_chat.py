import requests
import sys

BASE_URL = "http://localhost:8010/api"

def main():
    try:
        # Unlock placement
        placement_qs = requests.get(f"{BASE_URL}/placement/questions").json()
        ans = {q['id']: q['options'][0] for q in placement_qs if q['id'] <= 25} # Dummy answers
        requests.post(f"{BASE_URL}/placement/submit", json={"answers": ans})

        # Create session
        resp = requests.post(f"{BASE_URL}/sessions", json={"custom_topic": "Grammar Test"})
        if resp.status_code != 200:
             print(f"Session Create Error: {resp.text}")
             return
        sid = resp.json()['session_id']
        
        # Send bad grammar
        msg = "how is up m,y friend?"
        print(f"Sending: {msg}")
        reply = requests.post(f"{BASE_URL}/chat/{sid}/message", json={"text": msg}).json()
        
        print(f"Reply Text: {reply['reply']}")
        print(f"Errors: {reply['detected_errors']}")
        
        # Check that reply text does NOT contain "correction"
        low = reply['reply'].lower()
        if "correction" in low or "instead of" in low:
            print("WARNING: Reply might still contain spoken correction!")
        else:
            print("SUCCESS: Reply seems conversational.")
            
        # Check errors detected
        if len(reply['detected_errors']) > 0:
            print("SUCCESS: Errors detected in structured field.")
        else:
            print("WARNING: No errors detected (model might be lenient).")

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
