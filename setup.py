#!/usr/bin/env python3
"""
Setup script for Spotify Voice Assistant
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install some packages.")
        print("\nIf you're having trouble with pyaudio on Windows, try:")
        print("pip install pipwin")
        print("pipwin install pyaudio")
        return False

def check_config():
    """Check if config file is properly set up"""
    try:
        from config import CLIENT_ID, CLIENT_SECRET
        if CLIENT_ID == "your_client_id_here" or CLIENT_SECRET == "your_client_secret_here":
            print("\n⚠️  Configuration needed:")
            print("Please update config.py with your Spotify API credentials:")
            print("1. Go to https://developer.spotify.com/dashboard")
            print("2. Create a new app")
            print("3. Copy Client ID and Client Secret to config.py")
            print("4. Set redirect URI to: http://localhost:8080/callback")
            return False
        else:
            print("✓ Configuration looks good!")
            return True
    except ImportError:
        print("❌ config.py not found")
        return False

def main():
    print("Spotify Voice Assistant Setup")
    print("=============================")
    
    # Install requirements
    if install_requirements():
        print("\n" + "="*40)
        
        # Check configuration
        if check_config():
            print("\n🎉 Setup complete! You can now run:")
            print("python spotify_assistant.py")
        else:
            print("\n📝 Please complete the configuration steps above.")
    else:
        print("\n❌ Setup failed. Please install dependencies manually.")

if __name__ == "__main__":
    main()