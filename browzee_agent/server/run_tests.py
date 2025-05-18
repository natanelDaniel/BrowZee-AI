import subprocess
import time
import sys

def run_command(command):
    print(f"\n\n{'='*50}")
    print(f"Running: {command}")
    print(f"{'='*50}\n")
    
    process = subprocess.Popen(command, shell=True)
    process.wait()
    
    if process.returncode != 0:
        print(f"Command failed with exit code {process.returncode}")
        return False
    return True

def main():
    # First, set up the admin user and model
    print("Setting up admin user and sample model...")
    if not run_command("python setup_admin.py"):
        print("Setup failed. Exiting.")
        sys.exit(1)
    
    # Wait a bit for the server to process everything
    time.sleep(2)
    
    # Now run the API test as a normal user
    print("\nRunning API test as normal user...")
    if not run_command("python test_api.py"):
        print("API test failed. Exiting.")
        sys.exit(1)
    
    print("\n\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 