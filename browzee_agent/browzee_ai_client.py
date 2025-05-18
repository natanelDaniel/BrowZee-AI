"""
BrowZee AI API Client

A modular client for interacting with the BrowZee AI server API.
Handles authentication, model selection, and request processing.
"""

import httpx
import json
import asyncio
import base64
from contextlib import asynccontextmanager

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
        self._cleanup_lock = asyncio.Lock()
        self._closed = False
        
    async def initialize(self):
        """Initialize the API client and authenticate"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
            
        await self.authenticate()
        
    async def authenticate(self):
        """Authenticate with the server and get a JWT token"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
            
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            login_response = await self.client.post(f"{self.api_url}/auth/login", json=login_data)
            if login_response.status_code != 200:
                raise Exception(f"Authentication failed: {login_response.text}")
            
            user_auth = login_response.json()
            self.token = user_auth.get('token')
            
            if not self.token:
                raise Exception("No token received from login")
                
            # Load models for future use
            await self.get_models()
        except Exception as e:
            # Clean up client on authentication error
            await self._safe_close_client()
            raise e
        
    async def get_models(self):
        """Get available models from the server"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
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
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if not self.client:
            await self.initialize()
            
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
        
        try:
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
        except Exception as e:
            if "Event loop is closed" in str(e):
                # If event loop is closed, mark client as closed to prevent further operations
                self._closed = True
            raise e
    
    async def _safe_close_client(self):
        """Safely close the HTTP client with a lock to prevent race conditions"""
        async with self._cleanup_lock:
            if self.client and not self._closed:
                try:
                    await self.client.aclose()
                except Exception:
                    pass  # Ignore errors during cleanup
                finally:
                    self.client = None
                    self._closed = True
    
    async def close(self):
        """Close the HTTP client"""
        await self._safe_close_client()
        
    async def __aenter__(self):
        """Support for async context manager"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context"""
        await self.close()

    async def generate_vision(self, text: str, image_url: str, model_name: str = "Google Gemini Flash") -> str:
        """Generate a response using a vision model"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        model_name_lower = model_name.lower()
        if model_name_lower not in self.models_cache:
            await self.get_models()
            if model_name_lower not in self.models_cache:
                raise Exception(f"Model '{model_name}' not found")
                
        selected_model = self.models_cache[model_name_lower]
        
        # Handle URL conversion to base64 if needed
        if image_url.startswith('http'):
            base64_image = await get_image_as_base64(image_url)
            if not base64_image:
                raise Exception(f"Failed to convert image URL to base64: {image_url}")
            image_url = base64_image
        
        request_data = {
            "prompt": text,
            "image_url": image_url,
            "max_tokens": 1000
        }
        
        try:
            model_response = await self.client.post(
                f"{self.api_url}/models/{selected_model['_id']}/vision",
                headers=headers,
                json=request_data
            )
            
            if model_response.status_code != 200:
                raise Exception(f"Vision request failed: {model_response.text}")
            
            result = model_response.json()
            return self._extract_content(result, selected_model)
        except Exception as e:
            if "Event loop is closed" in str(e):
                self._closed = True
            raise e

    async def generate_structured(self, text: str, schema: dict, model_name: str = "Google Gemini Flash") -> dict:
        """Generate a structured response according to the provided JSON schema"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        model_name_lower = model_name.lower()
        if model_name_lower not in self.models_cache:
            await self.get_models()
            if model_name_lower not in self.models_cache:
                raise Exception(f"Model '{model_name}' not found")
                
        selected_model = self.models_cache[model_name_lower]
        
        request_data = {
            "prompt": text,
            "schema": schema,
            "max_tokens": 1000
        }
        
        try:
            model_response = await self.client.post(
                f"{self.api_url}/models/{selected_model['_id']}/structured",
                headers=headers,
                json=request_data
            )
            
            if model_response.status_code != 200:
                raise Exception(f"Structured request failed: {model_response.text}")
            
            result = model_response.json()
            return result['data']['output']
        except Exception as e:
            if "Event loop is closed" in str(e):
                self._closed = True
            raise e

    async def generate_structured_vision(self, text: str, image_url: str, schema: dict, model_name: str = "Google Gemini Flash") -> dict:
        """Generate a structured response from both text and image input"""
        if self._closed:
            raise RuntimeError("Client has been closed")
            
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        model_name_lower = model_name.lower()
        if model_name_lower not in self.models_cache:
            await self.get_models()
            if model_name_lower not in self.models_cache:
                raise Exception(f"Model '{model_name}' not found")
                
        selected_model = self.models_cache[model_name_lower]
        
        # Handle URL conversion to base64 if needed
        if image_url.startswith('http'):
            base64_image = await get_image_as_base64(image_url)
            if not base64_image:
                raise Exception(f"Failed to convert image URL to base64: {image_url}")
            image_url = base64_image
        
        request_data = {
            "prompt": text,
            "image_url": image_url,
            "schema": schema,
            "max_tokens": 1000
        }
        
        try:
            model_response = await self.client.post(
                f"{self.api_url}/models/{selected_model['_id']}/structured_vision",
                headers=headers,
                json=request_data
            )
            
            if model_response.status_code != 200:
                raise Exception(f"Structured vision request failed: {model_response.text}")
            
            result = model_response.json()
            return self._extract_content(result, selected_model)
        except Exception as e:
            if "Event loop is closed" in str(e):
                self._closed = True
            raise e

    def _extract_content(self, result: dict, model: dict) -> str:
        """Extract content from model response based on provider"""
        try:
            if model['provider'] == 'OPENAI':
                return result['data']['output']['choices'][0]['message']['content']
            elif model['provider'] == 'GEMINI':
                text = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
                # If the response is a JSON string enclosed in code blocks, extract it
                if text.startswith('```json') and text.endswith('```'):
                    json_text = text.replace('```json', '').replace('```', '').strip()
                    return json.loads(json_text)
                return text
            else:
                return json.dumps(result['data']['output'])
        except (KeyError, IndexError) as e:
            raise Exception(f"Error parsing response: {str(e)}")

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
    async with BrowzeeAIClient(email=email, password=password, api_url=api_url) as client:
        try:
            return await client.generate(prompt, model_name)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

# Helper function for vision requests
async def get_vision_response(prompt, image_url, email, password, model_name="Google Gemini Vision", api_url=API_BASE_URL):
    """
    Helper function to get a response from a vision model without managing a client.
    
    Args:
        prompt: The text prompt to send to the model
        image_url: URL of the image to analyze
        email: User email for authentication
        password: User password
        model_name: Name of the model to use (default: "Google Gemini Vision")
        api_url: API server URL (default: external ngrok URL)
        
    Returns:
        The model's text response or None if there was an error
    """
    async with BrowzeeAIClient(email=email, password=password, api_url=api_url) as client:
        try:
            return await client.generate_vision(prompt, image_url, model_name)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

# Helper function for structured vision requests
async def get_structured_vision_response(prompt, image_url, schema, email, password, model_name="Google Gemini Vision", api_url=API_BASE_URL):
    """
    Helper function to get a structured response from a vision model without managing a client.
    
    Args:
        prompt: The text prompt to send to the model
        image_url: URL of the image to analyze
        schema: JSON schema that defines the structure of the expected output
        email: User email for authentication
        password: User password
        model_name: Name of the model to use (default: "Google Gemini Vision")
        api_url: API server URL (default: external ngrok URL)
        
    Returns:
        The model's structured response (as a dict) or None if there was an error
    """
    async with BrowzeeAIClient(email=email, password=password, api_url=api_url) as client:
        try:
            return await client.generate_structured_vision(prompt, image_url, schema, model_name)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

# Helper function for structured text requests
async def get_structured_response(prompt, schema, email, password, model_name="Google Gemini Flash", api_url=API_BASE_URL):
    """
    Helper function to get a structured response from a text-only model without managing a client.
    
    Args:
        prompt: The text prompt to send to the model
        schema: JSON schema that defines the structure of the expected output
        email: User email for authentication
        password: User password
        model_name: Name of the model to use (default: "Google Gemini Flash")
        api_url: API server URL (default: external ngrok URL)
        
    Returns:
        The model's structured response (as a dict) or None if there was an error
    """
    async with BrowzeeAIClient(email=email, password=password, api_url=api_url) as client:
        try:
            return await client.generate_structured(prompt, schema, model_name)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

async def get_image_as_base64(image_url):
    """
    Get an image from a URL and convert it to base64
    
    Args:
        image_url: URL of the image to download
        
    Returns:
        Base64 encoded image with data URL prefix or None if failed
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            if response.status_code == 200:
                image_data = response.content
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_data}"
        except Exception as e:
            print(f"Error getting image: {str(e)}")
    return None 