import requests
import json
import sys
import httpx
import asyncio

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_model_request(email, password, prompt, model_name=None, base_url=None):
    """
    Test making a request to an AI model through the API.
    
    Args:
        email: User email for login
        password: User password
        prompt: The text prompt to send to the model
        model_name: Optional model name to use (will use first available if not specified)
        base_url: Optional base URL (default: localhost)
    """
    # Use custom base URL if provided
    api_url = base_url if base_url else BASE_URL
    
    print(f"Using API URL: {api_url}")
    print(f"Logging in as {email}...")
    
    # Login to get token
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{api_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    user_auth = response.json()
    token = user_auth.get('token')
    
    if not token:
        print("No token received from login")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get available models
    print("\nFetching available models...")
    response = requests.get(f"{api_url}/models", headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch models: {response.text}")
        return
    
    models_data = response.json()
    
    if models_data.get('count', 0) == 0:
        print("No models available. Please add some models first.")
        return
    
    models = models_data['data']
    print(f"Found {len(models)} models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model['name']} - {model['description']}")
    
    # Select model to use
    selected_model = None
    
    if model_name:
        # Find model by name
        for model in models:
            if model['name'].lower() == model_name.lower():
                selected_model = model
                break
        
        if not selected_model:
            print(f"Model '{model_name}' not found.")
            return
    else:
        # Use first available model
        selected_model = models[0]
    
    print(f"\nUsing model: {selected_model['name']}")
    
    # Make model request
    request_data = {
        "prompt": prompt,
        "max_tokens": 1000
    }
    
    print(f"Sending prompt: '{prompt}'")
    
    response = requests.post(
        f"{api_url}/models/{selected_model['_id']}/request", 
        headers=headers, 
        json=request_data
    )
    
    if response.status_code != 200:
        print(f"Request failed: {response.text}")
        return
    
    # Process and display the result
    result = response.json()
    
    print("\n--- MODEL RESPONSE ---")
    try:
        if selected_model['provider'] == 'OPENAI':
            content = result['data']['output']['choices'][0]['message']['content']
            print(content)
        elif selected_model['provider'] == 'GEMINI':
            content = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
            print(content)
        else:
            # Just print the raw output for unknown model types
            print(json.dumps(result['data']['output'], indent=2))
    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}")
        print("Raw response:")
        print(json.dumps(result, indent=2))

async def get_model_response(email, password, prompt, model_name="Google Gemini Flash", api_url=BASE_URL):
    """
    Async function to get a response from the model API server.
    
    Args:
        email: User email for login
        password: User password
        prompt: The text prompt to send to the model
        model_name: Model name to use (default: Google Gemini Flash)
        api_url: API server URL (default: localhost)
        
    Returns:
        The model's text response or None if there was an error
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = await client.post(f"{api_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return None
        
        user_auth = login_response.json()
        token = user_auth.get('token')
        
        if not token:
            print("No token received from login")
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get available models
        models_response = await client.get(f"{api_url}/models", headers=headers)
        if models_response.status_code != 200:
            print(f"Failed to fetch models: {models_response.text}")
            return None
        
        models_data = models_response.json()
        models = models_data.get('data', [])
        
        # Find requested model
        selected_model = None
        for model in models:
            if model['name'].lower() == model_name.lower():
                selected_model = model
                break
        
        if not selected_model:
            print(f"Model '{model_name}' not found.")
            return None
        
        # Make model request
        request_data = {
            "prompt": prompt,
            "max_tokens": 1000
        }
        
        model_response = await client.post(
            f"{api_url}/models/{selected_model['_id']}/request", 
            headers=headers, 
            json=request_data
        )
        
        if model_response.status_code != 200:
            print(f"Request failed: {model_response.text}")
            return None
        
        # Process and return the result
        result = model_response.json()
        
        try:
            # Extract content based on model provider
            if selected_model['provider'] == 'OPENAI':
                return result['data']['output']['choices'][0]['message']['content']
            elif selected_model['provider'] == 'GEMINI':
                return result['data']['output']['candidates'][0]['content']['parts'][0]['text']
            else:
                # For other model types, return as JSON string
                return json.dumps(result['data']['output'])
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {e}")
            return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_model_request.py <email> <password> <prompt> [model_name] [base_url]")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    prompt = sys.argv[3]
    model_name = sys.argv[4] if len(sys.argv) > 4 else None
    base_url = sys.argv[5] if len(sys.argv) > 5 else None
    
    test_model_request(email, password, prompt, model_name, base_url) 