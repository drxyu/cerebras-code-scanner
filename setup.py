#!/usr/bin/env python3
"""
Setup script for the Cerebras Code Scanner.

This script helps set up the environment for the Cerebras Code Scanner by checking
for the necessary environment variables and installing dependencies.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_environment():
    """Check if the necessary environment variables are set."""
    cerebras_api_key = os.environ.get("CEREBRAS_API_KEY")
    if not cerebras_api_key:
        print("\033[93mWarning: CEREBRAS_API_KEY environment variable is not set.\033[0m")
        print("You can set it by running: export CEREBRAS_API_KEY=your-api-key-here")
        print("Alternatively, you can add it to the config.json file.")
        
        # Check if key is in config.json
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                if config.get("cerebras_api_key"):
                    print("Found API key in config.json. You're good to go!")
                else:
                    print("No API key found in config.json either.")
            except Exception as e:
                print(f"Error reading config.json: {e}")
    else:
        print("✅ CEREBRAS_API_KEY environment variable is set.")

def install_dependencies():
    """Install the required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError installing dependencies: {e}\033[0m")
        return False
    return True

def create_logs_directory():
    """Create the logs directory if it doesn't exist."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Created logs directory.")
    else:
        print("✅ Logs directory already exists.")

def main():
    """Main function to set up the environment."""
    print("\n=== Cerebras Code Scanner Setup ===")
    
    # Check environment variables
    check_environment()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create logs directory
    create_logs_directory()
    
    print("\n=== Setup Complete ===")
    print("\nYou can now run the scanner with:")
    print("  python main.py --path /path/to/your/code")
    print("\nFor more options, run:")
    print("  python main.py --help")
    
    # Offer to run a sample scan
    sample_dir = Path("sample_code")
    if sample_dir.exists():
        print("\nWould you like to run a sample scan on the provided vulnerable code? (y/n)")
        choice = input("> ").strip().lower()
        if choice == "y":
            print("\nRunning sample scan...")
            subprocess.call([sys.executable, "main.py", "--path", "sample_code"])

if __name__ == "__main__":
    main()