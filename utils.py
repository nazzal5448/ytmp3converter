import yt_dlp
import uuid
import os
import asyncio
import dotenv as de
# Explicitly specify the path to .env
de.load_dotenv(dotenv_path="/opt/ytmp3converter/.env")

# Read cookies path
PATH = os.environ.get("COOKIES_PATH")
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
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'cachedir': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            
        }],
        'quiet': False,
        'noplaylist': True,
        'nocheckcertificate': True,
        'socket_timeout': 30,
        'cookiefile': PATH,
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
