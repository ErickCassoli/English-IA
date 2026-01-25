import requests
import json

try:
    resp = requests.get("http://localhost:8008/api/dashboard/summary")
    data = resp.json()
    print(json.dumps(data, indent=2))
    if 'study_time_total_seconds' in data:
        print("SUCCESS: Field found.")
    else:
        print("FAILURE: Field missing.")
except Exception as e:
    print(e)
