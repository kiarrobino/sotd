# Song of the Day (sotd)

## About
*sotd* is a python application that runs a `Discord` bot. The bot allows members of a server to play songs via `Youtube`. 

## Usage 

### Commands
#### Queue Management:
- `!add <url>` - Add a YouTube song to the queue
Example: !add https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot downloads the song and adds it to the queue
- `!queue` - Show what's currently playing and what's queued up
Displays now playing + all upcoming songs
- `!clear` - Clear the entire queue (removes all pending songs)
#### Playback Control:
- `!skip` - Skip the current song and play the next one
- `!stop` - Stop playback completely and clear the queue
- `!nowplaying`- Show what song is currently playing
#### Volume Control:
- `!volume <0-100>` - Set volume to a specific percentage
Example: !volume 50 sets volume to 50%
Example: !volume shows current volume without changing it
- `!volumeup`- Increase volume by 10%
- `!volumedown` - Decrease volume by 10%

### Example 
```
User1: !add https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot: Downloading from YouTube...
Bot: ✅ Added to queue (#1): Never Gonna Give You Up

User2: !volume 75
Bot: 🔊 Volume set to 75%

User2: !add https://www.youtube.com/watch?v=9bZkp7q19f0
Bot: ✅ Added to queue (#2): Gangnam Style

User1: !queue
Bot: 🎵 Now Playing: Never Gonna Give You Up
     Added by: User1#1234

     Queue:
     1. Gangnam Style
        Added by: User2#5678

User3: !volumeup
Bot: 🔊 Volume set to 85%

User1: !skip
Bot: ⏭️ Skipped!

User2: !nowplaying
Bot: 🎵 Now Playing: Gangnam Style
     Added by: User2#5678
```