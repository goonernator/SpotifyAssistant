#!/usr/bin/env python3
"""
Example usage of the Spotify Voice Assistant

This script demonstrates how to use the SpotifyAssistant class
and shows example voice commands.
"""

from spotify_assistant import SpotifyAssistant
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import time

def demo_assistant():
    """Demonstrate the assistant functionality"""
    print("Spotify Voice Assistant Demo")
    print("============================")
    
    # Create assistant instance
    assistant = SpotifyAssistant()
    
    # Check if credentials are configured
    if CLIENT_ID == "your_client_id_here":
        print("❌ Please configure your Spotify API credentials in config.py")
        print("Visit: https://developer.spotify.com/dashboard")
        return
    
    # Authenticate with Spotify
    print("\n🔐 Authenticating with Spotify...")
    if not assistant.authenticate_spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI):
        print("❌ Authentication failed. Please check your credentials.")
        return
    
    print("\n✅ Authentication successful!")
    print("\nHow to use: Say 'Spotify' to activate, then give your command when prompted.")
    print("Example: Say 'Spotify' → Wait for prompt → Say 'play'")
    print("\n=== Available Commands (after saying 'Spotify') ===")
    
    print("\n=== Basic Playback Controls ===")
    print("  • 'play' - Resume playback")
    print("  • 'pause' - Pause playback")
    print("  • 'skip' or 'next' - Skip to next track")
    print("  • 'previous' or 'back' - Go to previous track")
    
    print("\n=== Volume & Playback Options ===")
    print("  • 'volume [0-100]' - Set volume (e.g., 'volume 75')")
    print("  • 'shuffle on/off' - Toggle shuffle mode")
    print("  • 'repeat' - Repeat current track")
    print("  • 'repeat off' - Turn off repeat")
    
    print("\n=== Music Discovery ===")
    print("  • 'search and play [query]' - Search and play music")
    print("  • 'play artist [artist name]' - Play top songs by artist")
    print("  • 'play playlist [name]' - Play a specific playlist")
    print("  • 'play track [number]' - Play track number from current playlist")
    
    print("\n=== Library Management ===")
    print("  • 'like' or 'save' - Like current song")
    print("  • 'play liked' - Play your liked songs")
    
    print("\n=== Information ===")
    print("  • 'what song' - Get current song info")
    
    print("\n=== System ===")
    print("  • 'quit' - Exit the assistant")
    
    print("\n🎤 Starting voice recognition...")
    print("Make sure you have Spotify open on a device!")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Start the main listening loop
        assistant.start_listening()
    except KeyboardInterrupt:
        print("\n\n👋 Assistant stopped by user")
        assistant.speak("Goodbye!")

def test_commands():
    """Test individual commands programmatically"""
    print("\nTesting individual commands...")
    
    assistant = SpotifyAssistant()
    
    if CLIENT_ID == "your_client_id_here":
        print("❌ Please configure credentials first")
        return
    
    if assistant.authenticate_spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI):
        # Test different command types (without 'spotify' prefix since process_command expects it removed)
        test_commands_list = [
            "play",
            "pause", 
            "skip",
            "volume 50",
            "shuffle on",
            "what song",
            "search and play bohemian rhapsody",
            "play artist queen",
            "like",
            "play playlist discover weekly",
            "repeat",
            "shuffle off",
            "repeat off",
            "previous"
        ]
        
        print("\n🧪 Testing commands programmatically:")
        for cmd in test_commands_list:
            print(f"\nTesting: '{cmd}'")
            assistant.process_command(cmd)
            time.sleep(2)  # Wait between commands

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_commands()
    else:
        demo_assistant()