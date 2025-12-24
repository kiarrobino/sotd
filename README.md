# Song of the Day (sotd)

## About
*sotd* is a python application that runs a `Discord` bot. The bot allows members of a server to play songs via `Youtube`. 

## Usage 

### Commands
- `!add <url>` - Add a YouTube song to the queue
- `!queue` - See what's queued up
- `!skip` - Skip current song
- `!clear` - Clear the queue
- `!stop` - Stop everything
- `!nowplaying` - See what's playing

### Example 
```
User1: !add https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot: Downloading: Never Gonna Give You Up...
Bot: ✅ Added to queue (#1): Never Gonna Give You Up

User2: !add https://www.youtube.com/watch?v=9bZkp7q19f0
Bot: ✅ Added to queue (#2): Gangnam Style

User1: !queue
Bot: 🎵 Now Playing: Never Gonna Give You Up
     Added by: User1#1234

     Queue:
     1. Gangnam Style
        Added by: User2#5678

User3: !skip
Bot: ⏭️ Skipped!

User1: !nowplaying
Bot: 🎵 Now Playing: Gangnam Style
     Added by: User2#5678
```