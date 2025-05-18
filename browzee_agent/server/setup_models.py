import requests
import json
import pymongo
from bson import ObjectId

# Connection to MongoDB Atlas
CONNECTION_STRING = "mongodb+srv://netanel:LdwM41XfmTeN9wlm@cluster0.utf4e8z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "model-api"

# API base URL
BASE_URL = "http://localhost:5000/api"

# Model data
AI_MODELS = [
    {
        "name": "OpenAI GPT-4o",
        "description": "OpenAI's most advanced multimodal model capable of handling text and images.",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "parameters": {
            "model": "gpt-4o", 
            "temperature": 0.7
        },
        "provider": "OPENAI",
        "isPublic": True
    },
    {
        "name": "OpenAI GPT-4",
        "description": "OpenAI's advanced language model for complex tasks.",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "parameters": {
            "model": "gpt-4", 
            "temperature": 0.7
        },
        "provider": "OPENAI",
        "isPublic": True
    },
    {
        "name": "OpenAI GPT-3.5 Turbo",
        "description": "OpenAI's efficient and cost-effective model for most tasks.",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "parameters": {
            "model": "gpt-3.5-turbo", 
            "temperature": 0.7
        },
        "provider": "OPENAI",
        "isPublic": True
    },
    {
        "name": "Google Gemini Pro",
        "description": "Google's advanced multimodal model.",
        "endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
        "parameters": {},
        "provider": "GEMINI",
        "isPublic": True
    },
    {
        "name": "Google Gemini Flash",
        "description": "Google's faster Gemini variant.",
        "endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
        "parameters": {},
        "provider": "GEMINI",
        "isPublic": True
    },
    {
        "name": "XAI Grok-1",
        "description": "Xai's large language model.",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "parameters": {
            "model": "grok-1", 
            "temperature": 0.7
        },
        "provider": "XAI",
        "isPublic": True
    }
]

def setup_models():
    print("Setting up AI models...")
    
    try:
        # First, log in as admin
        login_data = {
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"Failed to login as admin: {response.text}")
            return
        
        admin_auth = response.json()
        admin_token = admin_auth.get('token')
        
        if not admin_token:
            print("No admin token received")
            return
            
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Add each model
        for model_data in AI_MODELS:
            # Check if model already exists
            exists = False
            
            response = requests.get(f"{BASE_URL}/models", headers=headers)
            if response.status_code == 200:
                models = response.json().get('data', [])
                for model in models:
                    if model.get('name') == model_data['name']:
                        print(f"Model '{model_data['name']}' already exists with ID: {model.get('_id')}")
                        exists = True
                        break
            
            if not exists:
                response = requests.post(f"{BASE_URL}/models", headers=headers, json=model_data)
                
                if response.status_code == 201 or response.status_code == 200:
                    print(f"Created model: {model_data['name']}")
                else:
                    print(f"Failed to create model {model_data['name']}: {response.text}")
        
        print("\nAll models setup completed!")
        
    except Exception as e:
        print(f"Setup failed with error: {str(e)}")

if __name__ == "__main__":
    setup_models() 