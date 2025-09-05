import spotipy
from spotipy.oauth2 import SpotifyOAuth
import speech_recognition as sr
import pyttsx3
import threading
import time
import re
from typing import Optional, List, Dict
from config import *

class SpotifyAssistant:
    def __init__(self):
        self.spotify = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.current_playlist_tracks = []
        
        # Configure TTS
        self.tts_engine.setProperty('rate', TTS_RATE)
        self.tts_engine.setProperty('volume', TTS_VOLUME)
        
        # Initialize microphone with error handling
        self.setup_microphone()
        
    def authenticate_spotify(self, client_id: str, client_secret: str, redirect_uri: str):
        """Authenticate with Spotify API"""
        try:
            scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-read-private,playlist-read-collaborative"
            
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope
            )
            
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
            print("Spotify authentication successful!")
            return True
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False
    
    def setup_microphone(self):
        """Initialize microphone with smart device selection and error handling"""
        print("🎤 Setting up microphone...")
        
        # Get list of available microphones
        try:
            mic_list = sr.Microphone.list_microphone_names()
            print(f"Found {len(mic_list)} audio devices")
        except Exception as e:
            print(f"❌ Failed to list microphones: {e}")
            self.microphone = None
            return
        
        # Look for common microphone names (prioritize Yeti first, then other microphones)
        preferred_mics = []
        yeti_mics = []
        
        for i, name in enumerate(mic_list):
            name_lower = name.lower()
            if 'yeti' in name_lower:
                yeti_mics.append((i, name))  # Highest priority for Yeti microphones
            elif any(keyword in name_lower for keyword in ['microphone', 'mic', 'blue', 'audio-technica', 'shure', 'rode']):
                if 'microphone' in name_lower and 'stereo' not in name_lower:
                    preferred_mics.insert(0, (i, name))  # Prioritize non-stereo microphones
                else:
                    preferred_mics.append((i, name))
        
        # Combine lists with Yeti microphones first
        preferred_mics = yeti_mics + preferred_mics
        
        # Try preferred microphones first
        for device_index, device_name in preferred_mics:
            if self._test_microphone(device_index, device_name):
                return
        
        # If no preferred mics work, try default
        print("\n🔄 Trying default microphone...")
        if self._test_microphone(None, "Default"):
            return
        
        # Last resort: try first few devices
        print("\n🔄 Trying first available devices...")
        for i in range(min(5, len(mic_list))):
            if self._test_microphone(i, mic_list[i]):
                return
        
        print("❌ No working microphone found!")
        self.microphone = None
    
    def _test_microphone(self, device_index, device_name):
        """Test if a specific microphone works"""
        try:
            print(f"Testing: {device_name}")
            if device_index is None:
                test_mic = sr.Microphone()
            else:
                test_mic = sr.Microphone(device_index=device_index)
            
            # Quick test
            with test_mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            self.microphone = test_mic
            print(f"✅ Successfully using: {device_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}...")
            return False
    
    def speak(self, text: str):
        """Print text without speaking (silent mode)"""
        print(f"Assistant: {text}")
    
    def wait_for_wake_word(self) -> bool:
        """Wait specifically for the wake word 'spotify'"""
        if self.microphone is None:
            print("No microphone available. Please check your microphone setup.")
            return False
            
        try:
            with self.microphone as source:
                # Minimal ambient noise adjustment for faster response
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                
                # Optimize energy threshold for better wake word detection
                self.recognizer.energy_threshold = 250
                self.recognizer.dynamic_energy_threshold = True
                
                # Reduced timeout for more responsive wake word detection
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=2)
                command = self.recognizer.recognize_google(audio).lower()
                
                if "spotify" in command:
                    print("✅ Spotify activated! What would you like me to do?")
                    return True
                else:
                    print(f"Heard: '{command}' - Please say 'Spotify' to activate.")
                    return False
                    
        except sr.WaitTimeoutError:
            # Don't print anything on timeout to reduce spam
            return False
        except sr.UnknownValueError:
            # Don't print anything when speech is unclear to reduce spam
            return False
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return False
        except Exception as e:
            print(f"Microphone error: {str(e)}")
            return False
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for voice commands after wake word is detected"""
        if self.microphone is None:
            print("No microphone available. Please check your microphone setup.")
            return None
            
        try:
            with self.microphone as source:
                # Reduced ambient noise adjustment for faster response
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                print("🎤 Listening for your command...")
                
                # Set energy threshold for better sensitivity
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                
                audio = self.recognizer.listen(source, timeout=VOICE_TIMEOUT, phrase_time_limit=VOICE_PHRASE_LIMIT)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"✅ Command received: {command}")
                return command
                    
        except sr.WaitTimeoutError:
            print("⏰ No command heard, going back to wake word detection...")
            return None
        except sr.UnknownValueError:
            print("❓ Sorry, I didn't understand that command. Please speak clearly.")
            return None
        except sr.RequestError as e:
            print(f"🌐 Could not request results; {e}")
            return None
        except Exception as e:
            print(f"🎤 Microphone error: {str(e)}")
            return None
    
    def get_available_devices(self):
        """Get list of available Spotify devices"""
        try:
            devices = self.spotify.devices()
            return devices['devices']
        except Exception as e:
            print(f"Failed to get devices: {str(e)}")
            return []
    
    def activate_device(self):
        """Find and activate an available Spotify device"""
        devices = self.get_available_devices()
        
        if not devices:
            print("❌ No Spotify devices found. Please open Spotify on a device.")
            return False
            
        # Look for an active device first
        for device in devices:
            if device['is_active']:
                print(f"✅ Using active device: {device['name']}")
                return True
        
        # If no active device, try to activate the first available one
        for device in devices:
            try:
                self.spotify.transfer_playback(device['id'], force_play=False)
                print(f"✅ Activated device: {device['name']}")
                time.sleep(1)  # Give it a moment to activate
                return True
            except Exception as e:
                print(f"Failed to activate {device['name']}: {str(e)}")
                continue
        
        print("❌ Could not activate any device")
        return False
    
    def play_music(self):
        """Resume playback"""
        try:
            self.spotify.start_playback()
            print("▶️ Playing music")
        except Exception as e:
            if "No active device" in str(e) or "404" in str(e):
                print("🔍 No active device found, searching for available devices...")
                if self.activate_device():
                    try:
                        self.spotify.start_playback()
                        print("▶️ Playing music")
                    except Exception as retry_e:
                        print(f"❌ Playback failed even after device activation: {str(retry_e)}")
                else:
                    print("❌ No active device found or playback failed")
            else:
                print(f"❌ Playback failed: {str(e)}")
    
    def pause_music(self):
        """Pause playback"""
        try:
            self.spotify.pause_playback()
            print("⏸️ Music paused")
        except Exception as e:
            if "No active device" in str(e) or "404" in str(e):
                print("🔍 No active device found for pause command")
                if self.activate_device():
                    try:
                        self.spotify.pause_playback()
                        print("⏸️ Music paused")
                    except Exception as retry_e:
                        print(f"❌ Pause failed: {str(retry_e)}")
                else:
                    print("❌ No device available to pause")
            else:
                print(f"❌ Pause failed: {str(e)}")
    
    def skip_track(self):
        """Skip to next track"""
        try:
            self.spotify.next_track()
            print("⏭️ Skipping to next track")
        except Exception as e:
            if "No active device" in str(e) or "404" in str(e):
                print("🔍 No active device found for skip command")
                if self.activate_device():
                    try:
                        self.spotify.next_track()
                        print("⏭️ Skipping to next track")
                    except Exception as retry_e:
                        print(f"❌ Skip failed: {str(retry_e)}")
                else:
                    print("❌ No device available to skip")
            else:
                print(f"❌ Skip failed: {str(e)}")
    
    def previous_track(self):
        """Go to previous track"""
        try:
            self.spotify.previous_track()
            print("Going to previous track")
        except Exception as e:
            print("Previous track failed")
    
    def set_volume(self, volume_percent: int):
        """Set playback volume (0-100)"""
        try:
            self.spotify.volume(volume_percent)
            print(f"Volume set to {volume_percent}%")
        except Exception as e:
            print(f"Failed to set volume: {str(e)}")
    
    def shuffle_on(self):
        """Turn shuffle on"""
        try:
            self.spotify.shuffle(True)
            print("Shuffle turned on")
        except Exception as e:
            print("Failed to turn on shuffle")
    
    def shuffle_off(self):
        """Turn shuffle off"""
        try:
            self.spotify.shuffle(False)
            print("Shuffle turned off")
        except Exception as e:
            print("Failed to turn off shuffle")
    
    def repeat_track(self):
        """Repeat current track"""
        try:
            self.spotify.repeat('track')
            print("Repeating current track")
        except Exception as e:
            print("Failed to set repeat")
    
    def repeat_off(self):
        """Turn off repeat"""
        try:
            self.spotify.repeat('off')
            print("Repeat turned off")
        except Exception as e:
            print("Failed to turn off repeat")
    
    def what_song(self):
        """Get current playing song info"""
        try:
            current = self.spotify.current_playback()
            if current and current['is_playing']:
                track = current['item']
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                album_name = track['album']['name']
                print(f"Now playing: {track_name} by {artist_name} from {album_name}")
            else:
                print("Nothing is currently playing")
        except Exception as e:
            print("Failed to get current song info")
    
    def play_artist(self, artist_name: str):
        """Play popular songs by an artist"""
        try:
            results = self.spotify.search(q=f'artist:{artist_name}', type='artist', limit=1)
            
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                artist_uri = artist['uri']
                artist_name_found = artist['name']
                
                # Get top tracks for the artist
                top_tracks = self.spotify.artist_top_tracks(artist_uri)
                if top_tracks['tracks']:
                    track_uris = [track['uri'] for track in top_tracks['tracks'][:10]]  # Top 10 tracks
                    try:
                        self.spotify.start_playback(uris=track_uris)
                        print(f"🎤 Playing top songs by {artist_name_found}")
                    except Exception as playback_e:
                        if "No active device" in str(playback_e) or "404" in str(playback_e):
                            print("🔍 No active device found, searching for available devices...")
                            if self.activate_device():
                                try:
                                    self.spotify.start_playback(uris=track_uris)
                                    print(f"🎤 Playing top songs by {artist_name_found}")
                                except Exception as retry_e:
                                    print(f"❌ Playback failed: {str(retry_e)}")
                            else:
                                print("❌ No device available to play music")
                        else:
                            print(f"❌ Playback failed: {str(playback_e)}")
                else:
                    print(f"❌ No tracks found for {artist_name}")
            else:
                print(f"❌ Artist '{artist_name}' not found")
                
        except Exception as e:
            print(f"❌ Failed to play artist: {str(e)}")
    
    def like_song(self):
        """Like/save the current song"""
        try:
            current = self.spotify.current_playback()
            if current and current['item']:
                track_id = current['item']['id']
                self.spotify.current_user_saved_tracks_add([track_id])
                track_name = current['item']['name']
                print(f"Liked: {track_name}")
            else:
                print("No song is currently playing")
        except Exception as e:
            print("Failed to like song")
    
    def play_liked_songs(self):
        """Play user's liked songs"""
        try:
            liked_tracks = self.spotify.current_user_saved_tracks(limit=50)
            if liked_tracks['items']:
                track_uris = [item['track']['uri'] for item in liked_tracks['items']]
                self.spotify.start_playback(uris=track_uris)
                print("Playing your liked songs")
            else:
                print("You don't have any liked songs")
        except Exception as e:
            print("Failed to play liked songs")
    
    def search_and_play(self, query: str):
        """Search for a song and play it"""
        try:
            results = self.spotify.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                
                try:
                    self.spotify.start_playback(uris=[track_uri])
                    print(f"🎵 Playing {track_name} by {artist_name}")
                except Exception as playback_e:
                    if "No active device" in str(playback_e) or "404" in str(playback_e):
                        print("🔍 No active device found, searching for available devices...")
                        if self.activate_device():
                            try:
                                self.spotify.start_playback(uris=[track_uri])
                                print(f"🎵 Playing {track_name} by {artist_name}")
                            except Exception as retry_e:
                                print(f"❌ Playback failed: {str(retry_e)}")
                        else:
                            print("❌ No device available to play music")
                    else:
                        print(f"❌ Playback failed: {str(playback_e)}")
            else:
                print(f"❌ Sorry, I couldn't find any songs matching '{query}'")
                
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
    
    def play_playlist(self, playlist_name: str):
        """Search and play a playlist"""
        try:
            results = self.spotify.search(q=playlist_name, type='playlist', limit=5)
            
            if results['playlists']['items']:
                # Find the best match
                for playlist in results['playlists']['items']:
                    if playlist_name.lower() in playlist['name'].lower():
                        playlist_uri = playlist['uri']
                        playlist_name_found = playlist['name']
                        
                        # Get playlist tracks for numbering
                        tracks = self.spotify.playlist_tracks(playlist_uri)
                        self.current_playlist_tracks = tracks['items']
                        
                        self.spotify.start_playback(context_uri=playlist_uri)
                        print(f"Playing playlist {playlist_name_found}")
                        return
                
                # If no exact match, play the first result
                playlist = results['playlists']['items'][0]
                playlist_uri = playlist['uri']
                playlist_name_found = playlist['name']
                
                tracks = self.spotify.playlist_tracks(playlist_uri)
                self.current_playlist_tracks = tracks['items']
                
                self.spotify.start_playback(context_uri=playlist_uri)
                print(f"Playing playlist {playlist_name_found}")
            else:
                print(f"Sorry, I couldn't find a playlist named {playlist_name}")
                
        except Exception as e:
            print(f"Playlist search failed: {str(e)}")
    
    def play_track_number(self, track_number: int):
        """Play a specific track number from current playlist"""
        try:
            if not self.current_playlist_tracks:
                print("No playlist is currently loaded")
                return
            
            if 1 <= track_number <= len(self.current_playlist_tracks):
                track = self.current_playlist_tracks[track_number - 1]['track']
                track_uri = track['uri']
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                
                self.spotify.start_playback(uris=[track_uri])
                print(f"Playing track {track_number}: {track_name} by {artist_name}")
            else:
                print(f"Track number {track_number} is not available. Playlist has {len(self.current_playlist_tracks)} tracks.")
                
        except Exception as e:
            print(f"Failed to play track number {track_number}: {str(e)}")
    
    def process_command(self, command: str):
        """Process voice commands"""
        command = command.lower().strip()
        
        if "play" in command and "playlist" in command:
            # Extract playlist name
            playlist_match = re.search(r'play playlist (.+)', command)
            if playlist_match:
                playlist_name = playlist_match.group(1)
                self.play_playlist(playlist_name)
            else:
                print("Please specify a playlist name")
        
        elif "play track" in command or "play number" in command:
            # Extract track number
            number_match = re.search(r'(?:track|number)\s+(\d+)', command)
            if number_match:
                track_number = int(number_match.group(1))
                self.play_track_number(track_number)
            else:
                print("Please specify a track number")
        
        elif "search" in command and "play" in command:
            # Extract search query
            search_match = re.search(r'search (?:and )?play (.+)', command)
            if search_match:
                query = search_match.group(1)
                self.search_and_play(query)
            else:
                print("Please specify what to search for")
        
        elif "play" in command:
            if any(word in command for word in ["song", "music", "track"]):
                # Extract song name
                play_match = re.search(r'play (?:song |music |track )?(.+)', command)
                if play_match:
                    query = play_match.group(1)
                    self.search_and_play(query)
            else:
                self.play_music()
        
        elif "pause" in command or "stop" in command:
            self.pause_music()
        
        elif "skip" in command or "next" in command:
            self.skip_track()
        
        elif "previous" in command or "back" in command:
            self.previous_track()
        
        elif "volume" in command:
            # Extract volume level
            volume_match = re.search(r'volume\s+(\d+)', command)
            if volume_match:
                volume = int(volume_match.group(1))
                if 0 <= volume <= 100:
                    self.set_volume(volume)
                else:
                    print("Volume must be between 0 and 100")
            else:
                print("Please specify a volume level (0-100)")
        
        elif "shuffle on" in command or "turn on shuffle" in command:
            self.shuffle_on()
        
        elif "shuffle off" in command or "turn off shuffle" in command:
            self.shuffle_off()
        
        elif "repeat" in command and "off" in command:
            self.repeat_off()
        
        elif "repeat" in command:
            self.repeat_track()
        
        elif "what song" in command or "current song" in command or "what's playing" in command:
            self.what_song()
        
        elif "play artist" in command:
            # Extract artist name
            artist_match = re.search(r'play artist (.+)', command)
            if artist_match:
                artist_name = artist_match.group(1)
                self.play_artist(artist_name)
            else:
                print("Please specify an artist name")
        
        elif "like" in command or "save" in command:
            self.like_song()
        
        elif "play liked" in command or "play favorites" in command or "play saved" in command:
            self.play_liked_songs()
        
        elif "quit" in command or "exit" in command or "stop listening" in command:
            print("Goodbye!")
            self.is_listening = False
        
        else:
            print("Sorry, I don't understand that command. Available commands: play, pause, skip, previous, volume, shuffle, repeat, what song, play artist, like, play liked songs, or quit.")
    
    def start_listening(self):
        """Start the voice command loop with wake word detection"""
        self.is_listening = True
        print("Spotify Assistant is ready!")
        print("Say 'Spotify' to activate, then give your command.")
        print("Available commands: play, pause, skip, previous, volume, shuffle, repeat, what song, play artist, like, play liked songs, quit")
        print("\n🎤 Listening for wake word 'Spotify'...")
        
        while self.is_listening:
            # First wait for wake word
            if self.wait_for_wake_word():
                # Then listen for the actual command
                command = self.listen_for_command()
                if command:
                    self.process_command(command)
                    print("\n🎤 Say 'Spotify' again to give another command...")
                else:
                    print("\n🎤 Listening for wake word 'Spotify'...")
            # Add a small delay to prevent excessive CPU usage
            time.sleep(0.5)

def main():
    print("Spotify Voice Assistant")
    print("=======================")
    print("Initializing...")
    
    assistant = SpotifyAssistant()
    
    # Check if microphone is available
    if assistant.microphone is None:
        print("\n❌ Microphone setup failed!")
        print("Please ensure:")
        print("1. A microphone is connected to your computer")
        print("2. Microphone permissions are granted")
        print("3. No other applications are using the microphone")
        return
    
    print("\n✅ Microphone setup successful!")
    print("\nSpotify API Setup:")
    print("Make sure you have:")
    print("1. Created a Spotify app at https://developer.spotify.com/dashboard")
    print("2. Set the redirect URI to http://localhost:8888/callback")
    print("3. Updated CLIENT_ID and CLIENT_SECRET in config.py")
    print()
    
    if CLIENT_ID == "your_client_id_here":
        print("Please update the CLIENT_ID and CLIENT_SECRET in config.py")
        return
    
    # Authenticate with Spotify
    if assistant.authenticate_spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI):
        print("\n🎵 Ready to start! Make sure to speak clearly into your microphone.")
        # Start listening for commands
        assistant.start_listening()
    else:
        print("\n❌ Spotify authentication failed. Please check your credentials.")

if __name__ == "__main__":
    main()