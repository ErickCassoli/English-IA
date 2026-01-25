import requests
import sys

BASE_URL = "http://localhost:8009/api"

def main():
    try:
        # 1. Reset (to clear recent)
        requests.delete(f"{BASE_URL}/admin/reset")
        
        # 2. Check Recent Topics (Should be default 3)
        print("Checking default topics...")
        topics = requests.get(f"{BASE_URL}/sessions/recent-topics").json()
        print(f"Got topics: {topics}")
        assert len(topics) == 3, f"Expected 3 default topics, got {len(topics)}"
        print("Defaults:", [t['code'] for t in topics])

        # 3. Create Custom Session (requires Assessment first?)
        # Ah, we have Strict Locking. We MUST be assessed first.
        # Let's bypass or do placement first.
        print("Passing placement test...")
        # (Assuming placement test is unlocked/reset works)
        # Actually reset clears assessment, so we are blocked.
        # Need to re-take placement via script logic
        placement_questions = requests.get(f"{BASE_URL}/placement/questions").json()
        perfect_answers = {q['id']: q['options'][0] for q in placement_questions} # Just dummy answers?
        # Need real answers to get >0 score? 
        # Actually for 403 unlock, any score > 0 might do? 
        # My placement logic requires >0 metrics. 
        # Let's use the verify_static_placement logic to submit meaningful answers
        answers = {
            1: "am", 2: "don't", 3: "What", 4: "His",
            5: "ate", 6: "taller", 7: "watching", 8: "any",
            9: "for", 10: "will stay", 11: "was", 12: "more", 13: "seeing",
            14: "were", 15: "had studied", 16: "will have finished", 17: "being", 18: "into",
            19: "have I seen", 20: "went", 21: "Omnipresent", 22: "of",
            23: "with", 24: "to", 25: "Succinct"
        }
        # Filter strictly
        valid_answers = {}
        for q in placement_questions:
             if q['id'] in answers:
                 valid_answers[q['id']] = answers[q['id']]
        
        requests.post(f"{BASE_URL}/placement/submit", json={"answers": valid_answers})

        # 4. Create Custom Session
        print("Creating custom session...")
        payload = {"custom_topic": "Space Exploration"}
        resp = requests.post(f"{BASE_URL}/sessions", json=payload)
        assert resp.status_code == 200, f"Custom creation failed: {resp.text}"
        sess_id = resp.json()['session_id']
        print(f"Session {sess_id} created with custom topic.")

        # 5. Check Recent Topics again (Should include 'custom' or the new topic)
        # NOTE: logic uses topic_code. Custom topics use code='custom'. 
        # So it might just show 'custom' once.
        topics_new = requests.get(f"{BASE_URL}/sessions/recent-topics").json()
        print("New Recents:", [t['label'] for t in topics_new])
        assert any(t['label'] == "Space Exploration" for t in topics_new), "Custom topic not in recents"

        print("ALL CHECKS PASSED")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
