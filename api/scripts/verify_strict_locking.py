import requests
import sys

BASE_URL = "http://localhost:8001/api"

def main():
    try:
        # 1. Reset
        print("Resetting data...")
        requests.post(f"{BASE_URL}/settings", json={"llm_provider": "simple_mock", "llm_model": "mock-1"})
        requests.delete(f"{BASE_URL}/admin/reset")

        # 2. Try to create normal session (Should FAIL)
        print("Attempting to create 'daily_life' session without assessment...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        if resp.status_code == 403:
            print("PASS: Access Forbidden (403) as expected.")
        else:
            print(f"FAIL: Expected 403, got {resp.status_code}")
            sys.exit(1)

        # 3. Try placement test (Should SUCCEED)
        print("Attempting to create 'placement_test' session...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "placement_test"})
        if resp.status_code == 200:
            print("PASS: Placement test allowed.")
            sid = resp.json()['session_id']
        else:
            print(f"FAIL: Expected 200, got {resp.status_code}")
            sys.exit(1)

        # 4. Finish Placement Test
        print("Finishing placement test...")
        resp = requests.post(f"{BASE_URL}/sessions/{sid}/finish")
        assert resp.status_code == 200, "Failed to finish session"

        # 5. Try creating normal session again (Should SUCCEED)
        print("Attempting to create 'daily_life' session WITH assessment...")
        resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        if resp.status_code == 200:
            print("PASS: Access Granted after assessment.")
        else:
            print(f"FAIL: Expected 200, got {resp.status_code}")
            sys.exit(1)

        print("\nALL CHECKS PASSED.")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
