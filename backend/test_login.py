import requests

url = "http://localhost:8001/api/login"
payload = {
    "email": "admin@raymond.in",
    "password": "@Pass123"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
