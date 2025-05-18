"""
This example shows how to modify the original code to use the BrowZee AI server API
instead of a direct model connection.
"""

import httpx
import asyncio
import json
from browzee_ai_client import BrowzeeAIClient, get_ai_response

# API base URL - using external ngrok URL
API_BASE_URL = "https://bf2d-34-31-229-185.ngrok-free.app/api"

# ORIGINAL CODE
"""
elif mode == "chat":
    # subprocess.run(
    #     ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"],
    #     cwd=str(COMPOSE_DIR),            #  <‑‑ מפעיל מתוך אותה תיקייה
    #     check=True
    # )
    # # 2. httpx client אחד לכל החיים
    # app.state.httpx = httpx.AsyncClient(timeout=30.0)

    messages = [
        HumanMessage(content=task_text)
    ]
    answer = await model.ainvoke(messages)
"""

# MODIFIED CODE TO USE THE SERVER API
async def get_model_response(email, password, prompt, model_name="Google Gemini Flash", api_url=API_BASE_URL):
    """
    Async function to get a response from the model API server.
    
    Args:
        email: User email for login
        password: User password
        prompt: The text prompt to send to the model
        model_name: Model name to use (default: Google Gemini Flash)
        api_url: API server URL (default: external ngrok URL)
        
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

# How to use this in your application:
async def example_function():
    # Your existing logic...
    
    if mode == "chat":
        # Set up server connection parameters
        EMAIL = "admin@example.com"  # Your user email
        PASSWORD = "Admin123!"  # Your password
        MODEL_NAME = "Google Gemini Flash"  # Model to use - works best externally
        
        # Instead of using a local model, call the API server
        # Extract the content from the message
        prompt = task_text
        if messages and hasattr(messages[0], 'content'):
            prompt = messages[0].content
        
        # Call the API server and get the response
        answer = await get_model_response(
            email=EMAIL,
            password=PASSWORD,
            prompt=prompt,
            model_name=MODEL_NAME
            # api_url is not specified, so it will use the default external URL
        )
        
        # Continue with your application logic using the answer...
        return answer

# Example of an API key-based approach that stores the token for reuse:
class ServerAPIClient:
    def __init__(self, email=None, password=None, api_url=API_BASE_URL):
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
    
    async def generate(self, prompt, model_name="Google Gemini Flash"):
        """Generate a response from the specified model"""
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
            "max_tokens": 1000
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
        if selected_model['provider'] == 'OPENAI':
            return result['data']['output']['choices'][0]['message']['content']
        elif selected_model['provider'] == 'GEMINI':
            return result['data']['output']['candidates'][0]['content']['parts'][0]['text']
        else:
            return json.dumps(result['data']['output'])
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

# Using the client in your application:
async def use_client_example():
    # Initialize once and reuse
    api_client = ServerAPIClient(
        email="admin@example.com",
        password="Admin123!"
        # Using default API_BASE_URL (external ngrok URL)
    )
    await api_client.initialize()
    
    # Now modify the chat mode to use this client
    if mode == "chat":
        # Extract prompt from messages
        prompt = task_text
        if messages and hasattr(messages[0], 'content'):
            prompt = messages[0].content
            
        # Get response from the API
        try:
            answer = await api_client.generate(prompt, "Google Gemini Flash")
            return answer
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None 

# Direct implementation for the original code (ready to copy/paste):
"""
elif mode == "chat":
    # Extract the content from messages
    prompt = task_text
    if isinstance(messages, list) and len(messages) > 0:
        if hasattr(messages[0], 'content'):
            prompt = messages[0].content
    
    # Use httpx to communicate with the external API
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login to get token
        login_data = {
            "email": "admin@example.com",  # Replace with your credentials
            "password": "Admin123!"
        }
        
        # Login using the external ngrok URL
        login_response = await client.post(
            "https://bf2d-34-31-229-185.ngrok-free.app/api/auth/login", 
            json=login_data
        )
        
        token = login_response.json().get('token')
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get models
        models_response = await client.get(
            "https://bf2d-34-31-229-185.ngrok-free.app/api/models", 
            headers=headers
        )
        
        # Find Gemini Flash model (most reliable for external access)
        models = models_response.json().get('data', [])
        gemini_model = None
        for model in models:
            if model['name'].lower() == "google gemini flash":
                gemini_model = model
                break
        
        # Make model request
        request_data = {
            "prompt": prompt,
            "max_tokens": 1000
        }
        
        model_response = await client.post(
            f"https://bf2d-34-31-229-185.ngrok-free.app/api/models/{gemini_model['_id']}/request",
            headers=headers,
            json=request_data
        )
        
        # Extract response
        result = model_response.json()
        answer = result['data']['output']['candidates'][0]['content']['parts'][0]['text']
""" 

# Example of how to use the BrowZee AI server API with the modular client.
# This shows how to modify the original code to use the API instead of direct model connection.

# Example 1: Simple one-line approach using helper function
async def simple_example(task_text):
    """
    The simplest approach - one function call to get AI response
    """
    # Extract content from message if needed
    prompt = task_text
    
    # Get response directly with one call
    return await get_ai_response(
        prompt=prompt,
        email="admin@example.com",
        password="Admin123!",
        model_name="Google Gemini Flash"
    )

# Example 2: Reusable client approach (recommended for multiple requests)
async def reusable_client_example(task_text):
    """
    Using a reusable client instance - best for multiple requests
    """
    # Create client just once and reuse it
    ai_client = BrowzeeAIClient(
        email="admin@example.com",
        password="Admin123!"
    )
    
    try:
        # Initialize once
        await ai_client.initialize()
        
        # Extract content from message if needed
        prompt = task_text
        
        # Make request with the initialized client
        return await ai_client.generate(prompt)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        # Always close the client when done
        await ai_client.close()

# Example 3: Direct replacement for the original code snippet
async def direct_replacement_example(mode, task_text, messages=None):
    """
    Direct replacement for the original code
    """
    if mode == "chat":
        # Extract prompt from messages
        prompt = task_text
        if messages and hasattr(messages[0], 'content'):
            prompt = messages[0].content
            
        # Use the helper function to get the response
        answer = await get_ai_response(
            prompt=prompt,
            email="admin@example.com",
            password="Admin123!"
        )
        
        return answer
    
    # Handle other modes as before
    return None

# Run the example if this script is executed directly
if __name__ == "__main__":
    async def run_examples():
        test_prompt = "Explain quantum computing in simple terms."
        
        print("Testing simple approach...")
        result1 = await simple_example(test_prompt)
        print(f"Result: {result1[:100]}...")
        
        print("\nTesting reusable client approach...")
        result2 = await reusable_client_example(test_prompt)
        print(f"Result: {result2[:100]}...")
    
    # Run the examples
    asyncio.run(run_examples()) 