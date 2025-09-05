# Spotify Voice Assistant

A Python-based voice-controlled Spotify assistant that responds to voice commands to control music playback, search for songs, and manage playlists.

## Features

- **Voice Commands**: Control Spotify using natural voice commands
- **Playback Control**: Play, pause, skip, and go to previous tracks
- **Search & Play**: Search for songs and artists by voice
- **Playlist Management**: Play playlists and select specific tracks by number
- **Text-to-Speech Feedback**: Audio confirmation of actions

## Prerequisites

1. **Spotify Premium Account**: Required for playback control
2. **Spotify Developer App**: Create at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
3. **Python 3.7+**: Make sure Python is installed
4. **Microphone**: For voice input
5. **Active Spotify Device**: Spotify app must be open on a device (computer, phone, etc.)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note for Windows users**: If you encounter issues installing `pyaudio`, try:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Set up Spotify API credentials**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Note your `Client ID` and `Client Secret`
   - Add `http://localhost:8888/callback` to your app's Redirect URIs
   - Update `config.py` with your credentials:
     ```python
     CLIENT_ID = "your_actual_client_id"
     CLIENT_SECRET = "your_actual_client_secret"
     ```
**Redirect URI can be set to whatever you please via config AND your developer portal**

## Usage

1. **Start the assistant**:
   ```bash
   python spotify_assistant.py
   ```

2. **First-time setup**: The app will open a browser for Spotify authentication

3. **Voice Commands**:

   **How it works:** First say "Spotify" to activate the assistant, then give your command when prompted.

   **Example:** Say "Spotify" → Wait for "What would you like me to do?" → Say "play"

   ### Basic Playback Controls
   - "play" - Resume playback
   - "pause" or "stop" - Pause playback
   - "skip" or "next" - Skip to next track
   - "previous" or "back" - Go to previous track

   ### Volume Control
   - "volume [0-100]" - Set volume to specific level (e.g., "volume 50")

   ### Playback Options
   - "shuffle on" or "turn on shuffle" - Enable shuffle mode
   - "shuffle off" or "turn off shuffle" - Disable shuffle mode
   - "repeat" - Repeat current track
   - "repeat off" - Turn off repeat

   ### Music Discovery & Search
   - "play [song name]" - Search and play a specific song
   - "search and play [artist/song]" - Search and play music
   - "play song [song name]" - Play a specific song
   - "play artist [artist name]" - Play top songs by an artist

   ### Playlist Management
   - "play playlist [playlist name]" - Play a specific playlist
   - "play track [number]" - Play track number from current playlist
   - "play number [number]" - Same as above

   ### Library Management
   - "like" or "save" - Like/save the current song
   - "play liked" or "play favorites" - Play your liked songs

   ### Information
   - "what song" or "current song" or "what's playing" - Get current song info

   ### Exit
   - "quit", "exit", or "stop listening" - Close the assistant

## Example Commands

```
"Spotify play playlist My Favorites"
"Spotify search and play Bohemian Rhapsody"
"Spotify play song Shape of You"
"Spotify play track 5"
"Spotify skip"
"Spotify pause"
"Spotify play"
```

## Configuration

You can modify settings in `config.py`:

- `VOICE_TIMEOUT`: Seconds to wait for voice input (default: 5)
- `VOICE_PHRASE_LIMIT`: Maximum seconds for a single phrase (default: 10)
- `TTS_RATE`: Text-to-speech rate in words per minute (default: 150)
- `TTS_VOLUME`: TTS volume level 0.0-1.0 (default: 0.8)

## Troubleshooting

### Common Issues

1. **"No active device found"**:
   - Make sure Spotify is open and playing on at least one device
   - Try playing a song manually first

2. **Authentication errors**:
   - Verify your Client ID and Client Secret are correct
   - Ensure redirect URI is set to `http://localhost:8080/callback`

3. **Microphone not working**:
   - Check your default microphone settings
   - Try running: `python -m speech_recognition` to test

4. **PyAudio installation issues**:
   - On Windows: Use `pipwin install pyaudio`
   - On macOS: `brew install portaudio` then `pip install pyaudio`
   - On Linux: `sudo apt-get install python3-pyaudio`

### Voice Recognition Tips

- Speak clearly and at a normal pace
- Minimize background noise
- Wait for "Listening for command..." before speaking
- If not recognized, try rephrasing the command

## Requirements

- spotipy==2.22.1
- SpeechRecognition==3.10.0
- pyttsx3==2.90
- pyaudio==0.2.11
- requests==2.31.0
- urllib3==2.0.4

## License

This project is for educational purposes. Make sure to comply with Spotify's Terms of Service when using their API.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
