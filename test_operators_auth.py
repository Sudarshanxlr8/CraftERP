import requests
import json

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3LCJ1c2VybmFtZSI6InJhbWVzaCIsInJvbGUiOiJPcGVyYXRvciIsImV4cCI6MTc1ODQ5MzIwOX0._tASVpGIoflMEw1WwHej_4fIj6KAaJMMtEfjdXyQfSU'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get('http://localhost:5000/api/operators', headers=headers)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Found {len(data)} operators')
        for op in data:
            print(f'- {op.get("username")} ({op.get("role")})')
except Exception as e:
    print(f'Error: {e}')