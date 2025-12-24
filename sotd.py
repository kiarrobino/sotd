import discord
from discord.ext import commands, tasks
import yt_dlp
import json
import os
from pathlib import Path
import subprocess
import asyncio
from queue import Queue
import time
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler

# Load environment variables
load_dotenv()

# Configure logging with Rich
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Queue file for sharing songs
QUEUE_FILE = 'music_queue.json'
DOWNLOAD_DIR = 'downloads'

# Create downloads directory
Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

# yt-dlp options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'keepvideo': False,
    'quiet': True,
    'no_warnings': True,
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicQueue:
    def __init__(self):
        self.load_queue()
    
    def load_queue(self):
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                self.queue = json.load(f)
        else:
            self.queue = []
    
    def save_queue(self):
        with open(QUEUE_FILE, 'w') as f:
            json.dump(self.queue, f, indent=2)
    
    def add_song(self, url, title, added_by, filepath):
        song = {
            'url': url,
            'title': title,
            'added_by': added_by,
            'filepath': filepath,
            'timestamp': time.time()
        }
        self.queue.append(song)
        self.save_queue()
    
    def get_next(self):
        if self.queue:
            song = self.queue.pop(0)
            self.save_queue()
            return song
        return None
    
    def get_all(self):
        return self.queue
    
    def clear(self):
        self.queue = []
        self.save_queue()

music_queue = MusicQueue()
currently_playing = None
player_process = None
is_playing = False

async def play_audio_local(filepath):
    # Play audio file on Raspberry Pi using mpg123
    global player_process
    
    logger.info(f"Attempting to play with mpg123: {filepath}")
    try:
        player_process = await asyncio.create_subprocess_exec(
            'mpg123', filepath,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await player_process.wait()
        player_process = None
        return
    except FileNotFoundError:
        logger.error("mpg123 not found")

@tasks.loop(seconds=2)
async def play_queue():
    # Background task to play songs from queue
    global currently_playing, is_playing
    
    if not is_playing and currently_playing is None:
        song = music_queue.get_next()
        if song:
            currently_playing = song
            is_playing = True
            logger.info(f"Now playing: {song['title']}")
            logger.info(f"File path: {song['filepath']}")
            
            try:
                # Play asynchronously
                await play_audio_local(song['filepath'])
                logger.info(f"Finished playing: {song['title']}")
                os.remove(song['filepath'])
                logger.info(f"Deleted: {song['filepath']}")
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
            
            currently_playing = None
            is_playing = False

@bot.event
async def on_ready():
    logger.info(f'{bot.user} successfully connected to Discord')
    play_queue.start()
    logger.info("K&S SOTD Bot started and ready to serve")

@bot.command(name='add', help='Add a YouTube song to the queue')
async def add(ctx, url):
    async with ctx.typing():
        try:
            # Extract info and download
            await ctx.send(f"Downloading from YouTube...")
            info = ytdl.extract_info(url, download=True)
            
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info['title']
            
            # Get the expected filename from yt-dlp
            filepath = ytdl.prepare_filename(info)
            # Change extension to .mp3 since we're converting
            filepath = os.path.splitext(filepath)[0] + '.mp3'
            
            # Wait a moment for file conversion to complete
            import time
            time.sleep(1)
            
            # Verify file exists
            if os.path.exists(filepath):
                music_queue.add_song(url, title, str(ctx.author), filepath)
                queue_pos = len(music_queue.get_all())
                await ctx.send(f"✅ Added to queue (#{queue_pos}): **{title}**")
            else:
                # List files in download dir for debugging
                files = os.listdir(DOWNLOAD_DIR)
                await ctx.send(f"❌ Error: Could not find downloaded file\nExpected: {filepath}\nFiles in dir: {files[:5]}")
                
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='queue', help='Show current queue')
async def show_queue(ctx):
    queue = music_queue.get_all()
    
    if currently_playing:
        msg = f"🎵 **Now Playing:** {currently_playing['title']}\n"
        msg += f"   Added by: {currently_playing['added_by']}\n\n"
    else:
        msg = "Nothing currently playing.\n\n"
    
    if queue:
        msg += "**Queue:**\n"
        for i, song in enumerate(queue, 1):
            msg += f"{i}. {song['title']}\n   Added by: {song['added_by']}\n"
    else:
        msg += "Queue is empty."
    
    await ctx.send(msg)

@bot.command(name='skip', help='Skip current song')
async def skip(ctx):
    global player_process, is_playing
    if player_process:
        player_process.terminate()
        player_process = None
        is_playing = False
        await ctx.send("⏭️ Skipped!")
    else:
        await ctx.send("Nothing is playing.")

@bot.command(name='clear', help='Clear the entire queue')
async def clear(ctx):
    music_queue.clear()
    await ctx.send("🗑️ Queue cleared!")

@bot.command(name='stop', help='Stop playback and clear queue')
async def stop(ctx):
    global player_process, currently_playing, is_playing
    if player_process:
        player_process.terminate()
        player_process = None
    music_queue.clear()
    currently_playing = None
    is_playing = False
    await ctx.send("⏹️ Stopped and cleared queue!")

@bot.command(name='nowplaying', help='Show currently playing song')
async def now_playing(ctx):
    if currently_playing:
        await ctx.send(f"🎵 **Now Playing:** {currently_playing['title']}\nAdded by: {currently_playing['added_by']}")
    else:
        await ctx.send("Nothing is currently playing.")

bot.run(os.getenv('DISCORD_TOKEN'))
