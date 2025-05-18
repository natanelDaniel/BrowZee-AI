"""
Test script for directly testing the Gemini API with structured data
"""
import httpx
import asyncio
import json
import os

# Gemini API base URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# Get API key from environment or use default test key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

async def test_gemini_direct():
    """Test the Gemini API directly with structured output instructions"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The person's full name"
                },
                "age": {
                    "type": "integer",
                    "description": "The person's age"
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["name", "age", "skills"]
        }
        
        # Request body for Gemini API
        request_data = {
            "contents": [
                {
                    "parts": [
                        { "text": "Create a profile for a fictional developer named John" }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            },
            "systemInstructions": {
                "parts": [
                    { 
                        "text": f"You must format your output as a JSON object that conforms to the following schema: {json.dumps(schema)}"
                    }
                ]
            }
        }
        
        # Endpoint with API key
        endpoint = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        
        print(f"Making request to Gemini API at {GEMINI_API_URL}...")
        print(f"Request data: {json.dumps(request_data, indent=2)}")
        
        # Make request
        response = await client.post(endpoint, json=request_data)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Request failed: {response.text}")
            return
        
        result = response.json()
        print(f"Success! Response: {json.dumps(result, indent=2)}")
        
        # Extract text from response
        try:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"\nExtracted JSON text: {text}")
            
            # Parse the JSON text
            parsed_json = json.loads(text)
            print(f"\nParsed JSON: {json.dumps(parsed_json, indent=2)}")
        except Exception as e:
            print(f"Error extracting or parsing JSON: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_gemini_direct()) 