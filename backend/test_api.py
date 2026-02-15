import requests

try:
    r = requests.get("http://localhost:8001/api/manpower")
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
    else:
        print(f"Success. Count: {len(r.json())}")
except Exception as e:
    print(f"Error: {e}")
