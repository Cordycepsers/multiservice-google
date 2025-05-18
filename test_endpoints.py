import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_root_endpoint():
    print("\nTesting root endpoint (GET /)")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

def test_webhook_endpoint_without_auth():
    print("\nTesting webhook endpoint without auth (POST /webhook)")
    test_data = {"message": "Hello from webhook"}
    response = requests.post(f"{BASE_URL}/webhook", json=test_data)
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

def main():
    print("Starting endpoint tests...")
    test_root_endpoint()
    test_webhook_endpoint_without_auth()
    print("\nTests completed!")

if __name__ == "__main__":
    main()
