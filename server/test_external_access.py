import requests
import socket
import json
import os
import sys

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

def test_external_access(base_url=None):
    """
    Test the API server's external accessibility
    
    Args:
        base_url: Optional external URL to test (e.g., ngrok URL)
    """
    if not base_url:
        # Get the local IP address if no URL is provided
        local_ip = get_local_ip()
        base_url = f"http://{local_ip}:5000"
    
    print(f"Testing server accessibility at: {base_url}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is accessible at the root endpoint")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to access server at the root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return
    
    # Test registration endpoint
    try:
        # Create a unique test user
        import random
        import string
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"external_test_{random_str}@example.com"
        
        user_data = {
            "name": "External Test User",
            "email": test_email,
            "password": "Password123!"
        }
        
        print(f"\nTesting user registration with email: {test_email}")
        response = requests.post(f"{base_url}/api/auth/register", json=user_data)
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Registration successful")
            user_auth = response.json()
            token = user_auth.get('token')
            api_key = user_auth.get('apiKey')
            
            print(f"Token received: {token[:10]}...")
            print(f"API key received: {api_key[:10]}...")
            
            # Test authenticated endpoints
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Get models
            print("\nTesting access to models endpoint")
            response = requests.get(f"{base_url}/api/models", headers=headers)
            
            if response.status_code == 200:
                models_data = response.json()
                model_count = models_data.get('count', 0)
                print(f"✅ Successfully retrieved {model_count} models")
                
                if model_count > 0:
                    print("Available models:")
                    for model in models_data.get('data', []):
                        print(f"- {model.get('name')}")
                        
                    # Test a model request
                    if models_data.get('data'):
                        model_id = models_data['data'][0]['_id']
                        print(f"\nTesting model request with model {model_id}")
                        
                        request_data = {
                            "prompt": "What is the capital of France?",
                            "max_tokens": 100
                        }
                        
                        response = requests.post(
                            f"{base_url}/api/models/{model_id}/request", 
                            headers=headers, 
                            json=request_data
                        )
                        
                        if response.status_code == 200:
                            print("✅ Model request successful")
                            print("Response sample (truncated):")
                            result = response.json()
                            if result.get('data', {}).get('output'):
                                print(f"Output: {str(result['data']['output'])[:200]}...")
                            else:
                                print(result)
                        else:
                            print(f"❌ Model request failed: {response.status_code}")
                            print(response.text)
            else:
                print(f"❌ Failed to retrieve models: {response.status_code}")
                print(response.text)
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print("\nExternal access test completed.")
    
    # Provide information for API usage
    print("\n=== API ACCESS INFORMATION ===")
    print(f"API Server URL: {base_url}")
    print("API Endpoints:")
    print(f"1. Register: POST {base_url}/api/auth/register")
    print(f"2. Login: POST {base_url}/api/auth/login")
    print(f"3. Get models: GET {base_url}/api/models")
    print(f"4. Make AI request: POST {base_url}/api/models/:id/request")

if __name__ == "__main__":
    # Check if URL is provided as command line argument
    if len(sys.argv) > 1:
        ngrok_url = sys.argv[1]
        test_external_access(ngrok_url)
    else:
        # Ask for ngrok URL
        ngrok_url = input("Enter ngrok URL (or press Enter to use local IP): ")
        if ngrok_url:
            test_external_access(ngrok_url)
        else:
            test_external_access() 