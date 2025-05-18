"""
Test the BrowzeeAIClient library directly
"""
import asyncio
from browzee_ai_client import BrowzeeAIClient

async def test_client():
    """Test the BrowzeeAIClient directly"""
    print("Creating client...")
    client = BrowzeeAIClient(
        email="admin@example.com",
        password="Admin123!",
        api_url="https://bf2d-34-31-229-185.ngrok-free.app/api"
    )
    
    try:
        print("Initializing client...")
        await client.initialize()
        
        print("Testing generate...")
        response1 = await client.generate("Tell me a short joke about programming.")
        print(f"Generate response: {response1}")
        
        # Test structured response with schema
        print("\nTesting generate_structured...")
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "skills": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["name", "age", "skills"]
        }
        
        try:
            response2 = await client.generate_structured(
                "Create a profile for a fictional developer named John",
                schema
            )
            print(f"Structured response: {response2}")
        except Exception as e:
            print(f"Error with structured request: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("\nClosing client...")
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_client()) 