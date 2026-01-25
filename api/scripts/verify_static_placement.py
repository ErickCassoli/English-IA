import requests
import sys

BASE_URL = "http://localhost:8006/api"

def main():
    try:
        # 1. Reset
        print("Resetting data...")
        requests.delete(f"{BASE_URL}/admin/reset")

        # 2. Check Assessment status (Should be False)
        dash = requests.get(f"{BASE_URL}/dashboard/summary").json()
        assert not dash['is_assessed'], "Should be unassessed initially"

        # 3. Create Session Should Fail
        print("Verifying lock...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        assert resp.status_code == 403, "Access should be forbidden"

        # 4. Fetch Questions
        print("Fetching placement questions...")
        questions = requests.get(f"{BASE_URL}/placement/questions").json()
        assert len(questions) > 0, "No questions returned"
        print(f"Got {len(questions)} questions")

        # 5. Submit Perfect Answers (C1/C2)
        print("Submitting perfect answers (C1 Level)...")
        # Hardcoding subset of answers for new 25-Q set
        answers = {
            1: "am", 2: "don't", 3: "What", 4: "His",
            5: "ate", 6: "taller", 7: "watching", 8: "any",
            9: "for", 10: "will stay", 11: "was", 12: "more", 13: "seeing",
            14: "were", 15: "had studied", 16: "will have finished", 17: "being", 18: "into",
            19: "have I seen", 20: "went", 21: "Omnipresent", 22: "of",
            23: "with", 24: "to", 25: "Succinct"
        }
        resp = requests.post(f"{BASE_URL}/placement/submit", json={"answers": answers})
        assert resp.status_code == 200, "Submission failed"
        result = resp.json()
        print(f"Result: {result}")
        assert result['score_pct'] == 100
        assert result['cefr_level'] == "C2" # Perfect score = C2 now

        # 6. Check Assessment status (Should be True)
        dash = requests.get(f"{BASE_URL}/dashboard/summary").json()
        assert dash['is_assessed'], "Should be assessed now"
        assert dash['fluency_level'] == "C1", f"Dasboard mismatch: {dash['fluency_level']}"

        # 7. Create Session Should Succeed
        print("Verifying unlock...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        assert resp.status_code == 200, "Should handle session creation now"

        print("\nALL CHECKS PASSED.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
