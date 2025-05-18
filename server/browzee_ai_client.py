"""
BrowZee AI API Client

A modular client for interacting with the BrowZee AI server API.
Handles authentication, model selection, and request processing.
"""

import httpx
import json

# API base URL - using external ngrok URL
API_BASE_URL = "https://bf2d-34-31-229-185.ngrok-free.app/api"

class BrowzeeAIClient:
    """Client for interacting with BrowZee AI API server"""
    
    def __init__(self, email=None, password=None, api_url=API_BASE_URL):
        """
        Initialize the BrowZee AI client.
        
        Args:
            email: User email for authentication
            password: User password
            api_url: API server URL (default: external ngrok URL)
        """
        self.api_url = api_url
        self.email = email
        self.password = password
        self.token = None
        self.client = None
        self.models_cache = {}
        
    async def initialize(self):
        """Initialize the API client and authenticate"""
        self.client = httpx.AsyncClient(timeout=30.0)
        await self.authenticate()
        
    async def authenticate(self):
        """Authenticate with the server and get a JWT token"""
        if not self.client:
            self.client = httpx.AsyncClient(timeout=30.0)
            
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        login_response = await self.client.post(f"{self.api_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            raise Exception(f"Authentication failed: {login_response.text}")
        
        user_auth = login_response.json()
        self.token = user_auth.get('token')
        
        if not self.token:
            raise Exception("No token received from login")
            
        # Load models for future use
        await self.get_models()
        
    async def get_models(self):
        """Get available models from the server"""
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        models_response = await self.client.get(f"{self.api_url}/models", headers=headers)
        if models_response.status_code != 200:
            raise Exception(f"Failed to fetch models: {models_response.text}")
        
        models_data = models_response.json()
        models = models_data.get('data', [])
        
        # Cache models by name for faster lookup
        self.models_cache = {model['name'].lower(): model for model in models}
        return models
    
    async def generate(self, prompt, model_name="Google Gemini Flash", max_tokens=1000):
        """
        Generate a response from the specified model.
        
        Args:
            prompt: The text prompt to send to the model
            model_name: Name of the model to use (default: "Google Gemini Flash")
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            The model's text response
        """
        if not self.token:
            await self.authenticate()
            
        # Get model ID
        model_name_lower = model_name.lower()
        if model_name_lower not in self.models_cache:
            await self.get_models()
            if model_name_lower not in self.models_cache:
                raise Exception(f"Model '{model_name}' not found")
                
        selected_model = self.models_cache[model_name_lower]
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        # Make request
        model_response = await self.client.post(
            f"{self.api_url}/models/{selected_model['_id']}/request", 
            headers=headers, 
            json=request_data
        )
        
        if model_response.status_code != 200:
            raise Exception(f"Request failed: {model_response.text}")
        
        # Process result
        result = model_response.json()
        
        # Extract content based on model provider
        try:
            if selected_model['provider'] == 'OPENAI':
                return result['data']['output']['choices'][0]['message']['content']
            elif selected_model['provider'] == 'GEMINI':
                return result['data']['output']['candidates'][0]['content']['parts'][0]['text']
            else:
                return json.dumps(result['data']['output'])
        except (KeyError, IndexError) as e:
            raise Exception(f"Error parsing response: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

# Simple helper function for one-off requests
async def get_ai_response(prompt, email, password, model_name="Google Gemini Flash", api_url=API_BASE_URL):
    """
    Simple helper function to get a response from the AI model without managing a client.
    
    Args:
        prompt: The text prompt to send to the model
        email: User email for authentication
        password: User password
        model_name: Name of the model to use (default: "Google Gemini Flash")
        api_url: API server URL (default: external ngrok URL)
        
    Returns:
        The model's text response or None if there was an error
    """
    client = BrowzeeAIClient(email=email, password=password, api_url=api_url)
    try:
        await client.initialize()
        return await client.generate(prompt, model_name)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        await client.close() 