"""
Simple test script for a regular model request
"""
import httpx
import asyncio
import json

# API base URL
API_BASE_URL = "https://bf2d-34-31-229-185.ngrok-free.app/api"

async def test_simple_request():
    """Test a regular model request"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_data = {
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        
        print(f"Logging in to {API_BASE_URL}/auth/login...")
        login_response = await client.post(f"{API_BASE_URL}/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        user_auth = login_response.json()
        token = user_auth.get('token')
        
        if not token:
            print("No token received from login")
            return
        
        print("Successfully logged in and got token")
        
        # Get models
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"Getting models from {API_BASE_URL}/models...")
        models_response = await client.get(f"{API_BASE_URL}/models", headers=headers)
        
        if models_response.status_code != 200:
            print(f"Failed to fetch models: {models_response.text}")
            return
        
        models = models_response.json().get('data', [])
        print(f"Found {len(models)} models")
        
        # Find suitable model
        model_name = "Google Gemini Flash"
        selected_model = None
        
        for model in models:
            print(f"Model: {model['name']} (ID: {model['_id']})")
            if model['name'].lower() == model_name.lower():
                selected_model = model
        
        if not selected_model:
            print(f"Model '{model_name}' not found.")
            return
        
        print(f"Selected model: {selected_model['name']} (ID: {selected_model['_id']})")
        
        # Request data - for a regular request
        request_data = {
            "prompt": "Tell me a short joke about programming.",
            "max_tokens": 1000
        }
        
        # Make regular request
        print(f"Making regular request to {API_BASE_URL}/models/{selected_model['_id']}/request...")
        print(f"Request data: {json.dumps(request_data, indent=2)}")
        
        response = await client.post(
            f"{API_BASE_URL}/models/{selected_model['_id']}/request", 
            headers=headers,
            json=request_data
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Request failed: {response.text}")
            return
        
        result = response.json()
        print(f"Success! Response data available.")
        
        # Try to extract the response text
        try:
            if selected_model['provider'] == 'OPENAI':
                content = result['data']['output']['choices'][0]['message']['content']
                print(f"Response text: {content}")
            elif selected_model['provider'] == 'GEMINI':
                content = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
                print(f"Response text: {content}")
            else:
                print(f"Raw response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Error extracting response: {e}")
            print(f"Raw response: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_simple_request()) 