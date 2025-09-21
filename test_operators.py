import requests
import json

# Test the operators endpoint
def test_operators_endpoint():
    try:
        # First, let's test with a simple GET request (no auth)
        print("Testing /api/operators endpoint...")
        response = requests.get('http://localhost:5000/api/operators')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("✓ Endpoint is accessible but requires authentication")
        elif response.status_code == 200:
            print("✓ Endpoint is working!")
            data = response.json()
            print(f"Found {len(data.get('users', []))} operators")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_operators_endpoint()