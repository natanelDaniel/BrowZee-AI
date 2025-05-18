"""
Test script for the vision API
"""
import httpx
import asyncio
import json
import base64
from urllib.request import urlopen
from urllib.parse import quote

# API base URL
API_BASE_URL = "https://bf2d-34-31-229-185.ngrok-free.app/api"

async def get_image_as_base64(image_url):
    """Get an image and convert it to base64"""
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        if response.status_code == 200:
            image_data = response.content
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_data}"
    return None

async def test_vision_api():
    """Test the vision API with various formats"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Login
        login_data = {
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        
        print(f"Logging in to {API_BASE_URL}/auth/login...")
        login_response = await client.post(f"{API_BASE_URL}/auth/login", json=login_data)
        
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
        
        # Prepare image
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/800px-Collage_of_Nine_Dogs.jpg"
        base64_image = await get_image_as_base64(image_url)
        
        if not base64_image:
            print(f"Failed to get image from {image_url}")
            return
        
        print(f"Got image data, first 50 chars: {base64_image[:50]}...")
        
        # Request data
        request_data = {
            "prompt": "What's in this image?",
            "image_url": base64_image
        }
        
        # Make vision request
        print(f"Making vision request to {API_BASE_URL}/models/{selected_model['_id']}/vision...")
        print(f"Request data (truncated): {json.dumps({k: v[:50] + '...' if k == 'image_url' else v for k, v in request_data.items()})}")
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/models/{selected_model['_id']}/vision", 
                headers=headers,
                json=request_data,
                timeout=60.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Request failed: {response.text}")
                return
            
            result = response.json()
            print(f"Success! Got response data")
            
            # Extract the response text
            try:
                content = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
                print(f"Response text: {content}")
            except (KeyError, IndexError) as e:
                print(f"Error extracting response: {e}")
                print(f"Raw response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Exception during request: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_vision_api()) 