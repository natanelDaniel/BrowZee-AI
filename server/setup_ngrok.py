"""
Script to set up Ngrok for exposing the API server to the internet.

First, install ngrok:
pip install pyngrok

Then run this script to create a tunnel to your local server.
"""

import os
import json
import time
from pyngrok import ngrok, conf

def setup_ngrok(port=5000, auth_token=None):
    """
    Set up an Ngrok tunnel to the specified port.
    
    Args:
        port: The local port your server is running on
        auth_token: Your Ngrok auth token (optional for free tier)
    """
    print("Setting up Ngrok tunnel...")
    
    # Set auth token if provided
    if auth_token:
        ngrok.set_auth_token(auth_token)
    
    # Create a tunnel to the local server
    public_url = ngrok.connect(port, "http")
    
    if isinstance(public_url, str):
        url = public_url
    else:
        url = public_url.public_url
    
    print(f"\n🌐 Server is now accessible globally at: {url}")
    print("This URL can be used from any device with internet access.")
    print("\nAPI Endpoints:")
    print(f"✅ Register: POST {url}/api/auth/register")
    print(f"✅ Login: POST {url}/api/auth/login")
    print(f"✅ Get Models: GET {url}/api/models")
    print(f"✅ Request AI: POST {url}/api/models/:id/request")
    
    # Save tunnel info to a file for reference
    tunnel_info = {
        "url": url,
        "local_port": port,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("ngrok_tunnel_info.json", "w") as f:
        json.dump(tunnel_info, f, indent=2)
    
    print("\nTunnel information saved to ngrok_tunnel_info.json")
    print("\nPress Ctrl+C to stop the tunnel when finished.")
    
    try:
        # Keep the tunnel open until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Ngrok tunnel...")
        ngrok.kill()
        print("Tunnel closed.")

if __name__ == "__main__":
    # Get Ngrok auth token if available
    auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    
    # You can also hardcode your auth token here if you prefer
    # auth_token = "your_ngrok_auth_token"
    
    setup_ngrok(port=5000, auth_token=auth_token) 