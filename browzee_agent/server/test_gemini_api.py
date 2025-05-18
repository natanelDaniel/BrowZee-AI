import requests
import json

# Gemini API key
API_KEY = "AIzaSyAQ29sFDclVfg40kHzArE7jpmBc8h3AdoU"

# Gemini API endpoint
ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"

def test_gemini_api():
    print("Testing direct connection to Google Gemini API...")
    
    # Create headers with API key
    headers = {
        "Content-Type": "application/json"
    }
    
    # Create request
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "What is the capital of France?"
                    }
                ]
            }
        ]
    }
    
    # Add API key as URL parameter
    url = f"{ENDPOINT}?key={API_KEY}"
    
    # Make request
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            try:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print("\nGemini Response:")
                print(text)
            except (KeyError, IndexError) as e:
                print(f"Error extracting text from response: {e}")
                print("Full response:")
                print(json.dumps(result, indent=2))
        else:
            print(f"API call failed: {response.text}")
            
    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        
if __name__ == "__main__":
    test_gemini_api() 