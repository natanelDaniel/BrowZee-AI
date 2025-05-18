import pymongo
from bson import ObjectId

# Connection to MongoDB Atlas
CONNECTION_STRING = "mongodb+srv://netanel:LdwM41XfmTeN9wlm@cluster0.utf4e8z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "model-api"

def update_model_endpoints():
    print("Updating model endpoints in the database...")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client[DB_NAME]
        models_collection = db["models"]
        
        # Update Gemini Pro endpoint to the correct model name
        result = models_collection.update_one(
            {"name": "Google Gemini Pro"},
            {"$set": {
                "endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-pro:generateContent",
                "parameters": {"model": "gemini-2.0-pro", "temperature": 0.7}
            }}
        )
        print(f"Updated Google Gemini Pro endpoint: {result.modified_count} document(s) modified")
        
        # Update Gemini Flash endpoint
        result = models_collection.update_one(
            {"name": "Google Gemini Flash"},
            {"$set": {
                "endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
                "parameters": {"model": "gemini-2.0-flash", "temperature": 0.7}
            }}
        )
        print(f"Updated Google Gemini Flash endpoint: {result.modified_count} document(s) modified")
        
        # Print updated models
        models = models_collection.find({"provider": "GEMINI"})
        for model in models:
            print(f"Model: {model['name']}, Endpoint: {model['endpoint']}")
        
        print("Model endpoints updated successfully!")
        
    except Exception as e:
        print(f"Update failed with error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    update_model_endpoints() 