import requests
import json
import time
import random
import string

# API base URL
BASE_URL = "http://localhost:5000/api"

def random_email():
    """Generate a random email for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def test_api():
    # Test data
    user_data = {
        "name": "Test User",
        "email": random_email(),
        "password": "Password123!"
    }
    
    print(f"Starting API test with {user_data['email']}")
    
    # STEP 1: Register a new user
    print("\n=== REGISTERING USER ===")
    register_url = f"{BASE_URL}/auth/register"
    response = requests.post(register_url, json=user_data)
    print(f"Status code: {response.status_code}")
    
    if response.status_code != 201 and response.status_code != 200:
        print(f"Error registering user: {response.text}")
        return
    
    user_auth = response.json()
    print(f"User registered successfully. Response: {json.dumps(user_auth, indent=2)}")
    
    token = user_auth.get('token')
    api_key = user_auth.get('apiKey')
    
    if not token:
        print("No token received from registration")
        return
    
    # Set up headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # STEP 2: Get current user details
    print("\n=== GETTING USER PROFILE ===")
    me_url = f"{BASE_URL}/auth/me"
    response = requests.get(me_url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"User profile: {json.dumps(user_info, indent=2)}")
    else:
        print(f"Error getting user profile: {response.text}")
    
    # STEP 3: Test API key authentication
    print("\n=== TESTING API KEY AUTHENTICATION ===")
    api_key_headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.get(me_url, headers=api_key_headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("API key authentication successful")
    else:
        print(f"API key authentication failed: {response.text}")
    
    # STEP 4: Get available models
    print("\n=== GETTING AVAILABLE MODELS ===")
    models_url = f"{BASE_URL}/models"
    response = requests.get(models_url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        models_data = response.json()
        print(f"Available models: {json.dumps(models_data, indent=2)}")
        
        if models_data.get('count', 0) > 0:
            # If there are models available, test making a request
            model_id = models_data['data'][0]['_id']
            
            print(f"\n=== MAKING A MODEL REQUEST TO {model_id} ===")
            request_url = f"{BASE_URL}/models/{model_id}/request"
            request_data = {
                "prompt": "Hello, AI model!",
                "max_tokens": 50
            }
            
            response = requests.post(request_url, headers=headers, json=request_data)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                request_result = response.json()
                print(f"Model request result: {json.dumps(request_result, indent=2)}")
            else:
                print(f"Error making model request: {response.text}")
    else:
        print(f"Error getting models: {response.text}")
    
    # STEP 5: Get request history
    print("\n=== GETTING REQUEST HISTORY ===")
    requests_url = f"{BASE_URL}/requests"
    response = requests.get(requests_url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        requests_data = response.json()
        print(f"Request history: {json.dumps(requests_data, indent=2)}")
    else:
        print(f"Error getting request history: {response.text}")
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"Test failed with error: {str(e)}") 