import requests
import sys

BASE_URL = "http://localhost:8010/api"

def main():
    try:
        # Get Practice Topics
        resp = requests.get(f"{BASE_URL}/practice/topics")
        topics = resp.json()
        print(f"Found {len(topics)} topics.")
        
        failed = False
        for t in topics:
            if t['code'].startswith("custom_"):
                print(f"FAIL: Found custom topic in list: {t['code']}")
                failed = True
            else:
                print(f"OK: {t['code']}")
        
        if failed:
            sys.exit(1)
            
        print("SUCCESS: No custom topics found.")
        
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
