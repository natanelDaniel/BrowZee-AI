import requests
import json
import pymongo
from bson import ObjectId
from urllib.parse import quote_plus

# Connection to MongoDB Atlas
CONNECTION_STRING = "mongodb+srv://netanel:LdwM41XfmTeN9wlm@cluster0.utf4e8z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "model-api"

# API base URL
BASE_URL = "http://localhost:5000/api"

def setup_admin_and_model():
    print("Setting up admin user and sample model...")
    
    # Create admin user directly in the database
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client[DB_NAME]
        users_collection = db["users"]
        
        # Check if admin already exists
        admin = users_collection.find_one({"email": "admin@example.com"})
        
        if admin:
            print(f"Admin user already exists with id: {admin['_id']}")
            admin_id = admin['_id']
            
            # Ensure the role is admin
            if admin.get('role') != 'admin':
                users_collection.update_one(
                    {"_id": admin_id},
                    {"$set": {"role": "admin"}}
                )
                print("Updated user to admin role")
        else:
            # Create admin user
            admin_data = {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "Admin123!",
                "role": "admin"  # This won't work through normal registration
            }
            
            # Register admin through API
            response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
            
            if response.status_code == 200 or response.status_code == 201:
                admin_auth = response.json()
                token = admin_auth.get('token')
                
                # Now get the admin user info
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                if response.status_code == 200:
                    admin_info = response.json()
                    user_id_str = admin_info['data']['_id']
                    admin_id = ObjectId(user_id_str)
                    
                    # Update the role to admin directly in the database
                    result = users_collection.update_one(
                        {"_id": admin_id},
                        {"$set": {"role": "admin"}}
                    )
                    
                    print(f"Created admin user with id: {user_id_str}")
                    print(f"Admin role update result: {result.modified_count} document(s) modified")
                    print(f"Admin token: {token}")
                else:
                    print(f"Failed to get user info: {response.text}")
                    return
            else:
                print(f"Failed to create admin user: {response.text}")
                return
        
        # Verify admin role was set correctly
        admin = users_collection.find_one({"email": "admin@example.com"})
        if admin and admin.get('role') == 'admin':
            print(f"Confirmed user has admin role: {admin.get('role')}")
        else:
            print(f"WARNING: User does not have admin role! Current role: {admin.get('role')}")
            return
            
        # Login as admin
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
        
        # Create a sample model
        print("\nCreating a sample model...")
        
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # First, check if model already exists
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to check existing models: {response.text}")
            return
        
        models_data = response.json()
        
        if models_data.get('count', 0) > 0:
            print("Model already exists:")
            for model in models_data.get('data', []):
                print(f"- {model.get('name')}: {model.get('_id')}")
        else:
            # Create a sample model
            model_data = {
                "name": "Sample GPT Model",
                "description": "A sample model for testing",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "parameters": {
                    "model": "gpt-3.5-turbo", 
                    "temperature": 0.7
                },
                "provider": "OPENAI",
                "isPublic": True
            }
            
            response = requests.post(f"{BASE_URL}/models", headers=headers, json=model_data)
            
            if response.status_code == 201 or response.status_code == 200:
                model_info = response.json()
                print(f"Created sample model: {json.dumps(model_info, indent=2)}")
            else:
                print(f"Failed to create sample model: {response.text}")
        
        print("\nSetup completed successfully!")
        
    except Exception as e:
        print(f"Setup failed with error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    setup_admin_and_model() 