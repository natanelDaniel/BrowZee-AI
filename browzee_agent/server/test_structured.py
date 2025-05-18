"""
Test script for structured output and vision features
"""
import asyncio
from browzee_ai_client import (
    BrowzeeAIClient, 
    get_ai_response, 
    get_vision_response,
    get_structured_response, 
    get_structured_vision_response
)
import json

# Example schema for structured output
PERSON_SCHEMA = {
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
        "occupation": {
            "type": "string",
            "description": "The person's job or profession"
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of skills the person has"
        }
    },
    "required": ["name", "age", "occupation", "skills"]
}

async def test_structured_output():
    """Test structured output response"""
    print("\n=== Testing Structured Output ===")
    prompt = "Create a profile for a fictional software developer named John Smith who is 32 years old."
    
    result = await get_structured_response(
        prompt=prompt,
        schema=PERSON_SCHEMA,
        email="admin@example.com",
        password="Admin123!"
    )
    
    print(f"Structured Response: {result}")
    
    # Extract JSON from the response if needed
    parsed_result = result
    if isinstance(result, dict) and 'candidates' in result:
        try:
            # Extract the text content
            text = result['candidates'][0]['content']['parts'][0]['text']
            # If it's JSON in code blocks, parse it
            if text.startswith('```json') and text.endswith('```'):
                json_text = text.replace('```json', '').replace('```', '').strip()
                parsed_result = json.loads(json_text)
                print(f"Parsed JSON: {parsed_result}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON: {e}")
    
    # Access specific fields from parsed result
    if isinstance(parsed_result, dict):
        print(f"Name: {parsed_result.get('name')}")
        print(f"Age: {parsed_result.get('age')}")
        print(f"Occupation: {parsed_result.get('occupation')}")
        print(f"Skills: {', '.join(parsed_result.get('skills', []))}")

async def test_vision():
    """Test vision response"""
    print("\n=== Testing Vision API ===")
    prompt = "What's in this image?"
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/800px-Collage_of_Nine_Dogs.jpg"
    
    # Use the Flash model which we know exists
    result = await get_vision_response(
        prompt=prompt,
        image_url=image_url,
        email="admin@example.com",
        password="Admin123!",
        model_name="Google Gemini Flash"  # Use the model we know exists
    )
    
    print(f"Vision Response: {result[:200]}...")

async def test_structured_vision():
    """Test structured vision response"""
    print("\n=== Testing Structured Vision ===")
    
    # Schema for image analysis
    image_schema = {
        "type": "object",
        "properties": {
            "main_subject": {
                "type": "string",
                "description": "The main subject of the image"
            },
            "colors": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Dominant colors in the image"
            },
            "objects": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Objects visible in the image"
            },
            "description": {
                "type": "string",
                "description": "Brief description of the image"
            }
        },
        "required": ["main_subject", "colors", "objects", "description"]
    }
    
    prompt = "Analyze this image and provide details about it"
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/800px-Collage_of_Nine_Dogs.jpg"
    
    # Use the Flash model which we know exists
    result = await get_structured_vision_response(
        prompt=prompt,
        image_url=image_url,
        schema=image_schema,
        email="admin@example.com",
        password="Admin123!",
        model_name="Google Gemini Flash"  # Use the model we know exists
    )
    
    print(f"Structured Vision Response: {result}")
    
    # Extract JSON from the response if needed
    parsed_result = result
    if isinstance(result, dict) and 'candidates' in result:
        try:
            # Extract the text content
            text = result['candidates'][0]['content']['parts'][0]['text']
            # If it's JSON in code blocks, parse it
            if text.startswith('```json') and text.endswith('```'):
                json_text = text.replace('```json', '').replace('```', '').strip()
                parsed_result = json.loads(json_text)
                print(f"Parsed JSON: {parsed_result}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON: {e}")
    
    # Access specific fields from parsed result
    if isinstance(parsed_result, dict):
        print(f"Main Subject: {parsed_result.get('main_subject')}")
        print(f"Colors: {', '.join(parsed_result.get('colors', []))}")
        print(f"Objects: {', '.join(parsed_result.get('objects', []))}")
        print(f"Description: {parsed_result.get('description')}")

async def main():
    """Run all tests"""
    try:
        await test_structured_output()
        await test_vision()
        await test_structured_vision()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 