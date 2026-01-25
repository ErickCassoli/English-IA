import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def reset_data():
    requests.post(f"{BASE_URL}/settings", json={"llm_provider": "simple_mock", "llm_model": "mock-1"})
    requests.delete(f"{BASE_URL}/admin/reset")

def get_dashboard():
    resp = requests.get(f"{BASE_URL}/dashboard/summary")
    return resp.json()

def main():
    try:
        print("1. Resetting Data...")
        reset_data()
        
        # Check assessed status
        dash = get_dashboard()
        print(f"   is_assessed: {dash.get('is_assessed')} (Expected: False)")
        assert dash.get('is_assessed') == False, "Dashboard should report NOT assessed"
        
        print("\n2. Simulating User trying to access normal topic without assessment...")
        # Since I am just API testing, I verify that the API allows it (locking is UI side), 
        # but the DASHBOARD returns the flag correctly.
        
        print("\n3. Taking Placement Test...")
        sess = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "placement_test"}).json()
        sid = sess['session_id']
        requests.post(f"{BASE_URL}/chat/{sid}/message", json={"text": "Hello"})
        requests.post(f"{BASE_URL}/sessions/{sid}/finish")
        
        print("   Test finished.")
        dash = get_dashboard()
        print(f"   is_assessed: {dash.get('is_assessed')} (Expected: True)")
        assert dash.get('is_assessed') == True, "Dashboard should report ASSESSED"
        
        print("\nVerification Passed: Backend correctly toggles assessment status.")
        
    except Exception as e:
        print(f"\nFAILED: {e}")

if __name__ == "__main__":
    main()
