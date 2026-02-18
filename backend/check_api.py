import requests
import time

url = "http://localhost:8001/api/manpower"

try:
    print(f"GET {url}...")
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Received {len(data)} records.")
        if len(data) > 0:
            print("Sample record:", data[0])
    else:
        print("Failed to fetch data.")
        print(response.text)
except Exception as e:
    print(f"Error checking API: {e}")
