import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

RC_NUMBER = "rj27cm8183"
API_URL = "http://localhost:8080/api/v1/idv/gemini"

payload = {
    "rc_number": RC_NUMBER
}

print(f"Calling RC API for: {RC_NUMBER}")
print(f"URL: {API_URL}\n")

try:
    response = requests.post(API_URL, json=payload, timeout=30)
    
    print(f"Status Code: {response.status_code}\n")
    
    result = response.json()
    print("Response:")
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"Error: {str(e)}")
