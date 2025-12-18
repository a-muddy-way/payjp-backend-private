import requests
import json

try:
    response = requests.post(
        "http://localhost:5001/purchase",
        json={"book_id": 1},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(e)
