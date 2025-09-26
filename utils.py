import yt_dlp
import uuid
import os
import asyncio
import dotenv as de
# Explicitly specify the path to .env
de.load_dotenv(dotenv_path="/opt/ytmp3converter/.env")

# de.load_dotenv()

# Read cookies path
PATH = os.environ.get("COOKIES_PATH")
print(f"Getting cookies from: {PATH}")
print(f"File exists? {os.path.exists(PATH)}")
print(f"Readable? {os.access(PATH, os.R_OK)}")
print(f"Getting cookies from: {PATH}")
if not PATH or not os.path.exists(PATH):
    raise RuntimeError(f"Cookies file not found at {PATH}")

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def download_and_convert(url: str):
    if "youtube.com" not in url and "youtu.be" not in url:
        raise ValueError("Invalid YouTube URL")

    video_id = str(uuid.uuid4())
    output_path = os.path.join(TEMP_DIR, f"{video_id}.%(ext)s")
    final_mp3_path = os.path.join(TEMP_DIR, f"{video_id}.mp3")

    ydl_opts = {
    "format": "bestaudio",   # match CLI -f bestaudio
    "outtmpl": output_path,
    "cookiefile": PATH,
    "noplaylist": True,
    "nocheckcertificate": True,
    "socket_timeout": 30,
    "cachedir": False,
    "quiet": False,

    # Equivalent of --extract-audio --audio-format mp3
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],

    # Add this: force yt-dlp to prefer ffmpeg directly if HLS/SABR is forced
    "prefer_ffmpeg": True,
    }


    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        if not os.path.exists(final_mp3_path):
            raise RuntimeError("Conversion failed: MP3 file was not created.")

        return final_mp3_path, os.path.basename(final_mp3_path)

    except yt_dlp.utils.DownloadError as de:
        raise RuntimeError("The video is unavailable, private, geo-blocked, or rate-limited.") from de

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")

def cleanup_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Cleanup failed for {path}: {e}")
