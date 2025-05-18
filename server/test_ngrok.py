import requests
import json
import sys
import time

# Default ngrok URL - replace this with your actual ngrok URL
DEFAULT_NGROK_URL = "https://bf2d-34-31-229-185.ngrok-free.app"

def test_ngrok_api(ngrok_url=None):
    """
    Test the API through the ngrok URL
    
    Args:
        ngrok_url: The ngrok URL to test
    """
    if not ngrok_url:
        ngrok_url = DEFAULT_NGROK_URL
    
    # Remove trailing slash if present
    if ngrok_url.endswith('/'):
        ngrok_url = ngrok_url[:-1]
        
    print(f"Testing API via ngrok at: {ngrok_url}")
    print("-" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{ngrok_url}/")
        print("Health Check:", end=" ")
        if response.status_code == 200:
            print("✅ Success")
            print(f"Server info: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return
    
    # Test 2: Register a new user
    print("\nRegistering a new user...", end=" ")
    
    # Create unique username
    import random
    import string
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"ngrok_test_{random_str}@example.com"
    
    user_data = {
        "name": "Ngrok Test User",
        "email": test_email,
        "password": "Password123!"
    }
    
    try:
        response = requests.post(f"{ngrok_url}/api/auth/register", json=user_data)
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Success")
            user_auth = response.json()
            token = user_auth.get('token')
            api_key = user_auth.get('apiKey')
            
            print(f"Registered user: {test_email}")
            print(f"Token: {token[:15]}...")
            print(f"API Key: {api_key[:15]}...")
            
            # Set up headers for authenticated requests
            jwt_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            apikey_headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            # Test 3: Get profile with JWT
            print("\nGetting user profile with JWT...", end=" ")
            try:
                response = requests.get(f"{ngrok_url}/api/auth/me", headers=jwt_headers)
                if response.status_code == 200:
                    print("✅ Success")
                    user_info = response.json()
                    print(f"User: {user_info['data']['name']} ({user_info['data']['email']})")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Test 4: Get profile with API Key
            print("\nGetting user profile with API Key...", end=" ")
            try:
                response = requests.get(f"{ngrok_url}/api/auth/me", headers=apikey_headers)
                if response.status_code == 200:
                    print("✅ Success")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Test 5: Get available models
            print("\nFetching available models...", end=" ")
            try:
                response = requests.get(f"{ngrok_url}/api/models", headers=jwt_headers)
                if response.status_code == 200:
                    models_data = response.json()
                    model_count = models_data.get('count', 0)
                    print(f"✅ Success - Found {model_count} models")
                    
                    # Test 6: Make a model request if models are available
                    if model_count > 0:
                        models = models_data.get('data', [])
                        print("Available models:")
                        for i, model in enumerate(models):
                            print(f"{i+1}. {model.get('name')} ({model.get('provider', 'unknown')})")
                        
                        # Find a suitable model for testing
                        test_model = None
                        
                        # Try to find models in this order of preference
                        for provider in ['OPENAI', 'XAI', 'GEMINI']:
                            for model in models:
                                if model.get('provider') == provider:
                                    test_model = model
                                    break
                            if test_model:
                                break
                        
                        # If no suitable model found, use the first one
                        if not test_model:
                            test_model = models[0]
                        
                        print(f"\nTesting model request with: {test_model.get('name')}")
                        
                        request_data = {
                            "prompt": "What is the capital of France? Answer in one word.",
                            "max_tokens": 50
                        }
                        
                        try:
                            response = requests.post(
                                f"{ngrok_url}/api/models/{test_model['_id']}/request", 
                                headers=jwt_headers, 
                                json=request_data
                            )
                            if response.status_code == 200:
                                print("✅ Model request successful!")
                                result = response.json()
                                print("\n--- MODEL RESPONSE ---")
                                
                                # Extract the content based on the model provider
                                try:
                                    if test_model.get('provider') == 'OPENAI':
                                        content = result['data']['output']['choices'][0]['message']['content']
                                        print(content)
                                    elif test_model.get('provider') == 'GEMINI':
                                        content = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
                                        print(content)
                                    else:
                                        print(json.dumps(result['data']['output'], indent=2))
                                except (KeyError, IndexError) as e:
                                    print(f"Error parsing response: {e}")
                                    print("Raw response:")
                                    print(json.dumps(result, indent=2))
                                
                            else:
                                print(f"❌ Model request failed with status {response.status_code}")
                                print(response.text)
                        except Exception as e:
                            print(f"❌ Error making model request: {str(e)}")
                    else:
                        print("No models available to test.")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("External ngrok API test completed!")
    print("=" * 50)
    print(f"Your API is now accessible worldwide at: {ngrok_url}")
    print("API Endpoints:")
    print(f"✅ Register: POST {ngrok_url}/api/auth/register")
    print(f"✅ Login: POST {ngrok_url}/api/auth/login")
    print(f"✅ Get Models: GET {ngrok_url}/api/models")
    print(f"✅ Request AI: POST {ngrok_url}/api/models/:id/request")

if __name__ == "__main__":
    # Get ngrok URL from command line argument or use the default
    if len(sys.argv) > 1:
        ngrok_url = sys.argv[1]
        test_ngrok_api(ngrok_url)
    else:
        # Ask for ngrok URL
        ngrok_url = input(f"Enter ngrok URL (or press Enter to use default: {DEFAULT_NGROK_URL}): ")
        if ngrok_url:
            test_ngrok_api(ngrok_url)
        else:
            test_ngrok_api() 