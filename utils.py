import yt_dlp
import uuid
import os
import asyncio
import dotenv as de
import logging

# Explicitly specify the path to .env
de.load_dotenv(dotenv_path="/opt/ytmp3converter/.env")

# Logger setup
logger = logging.getLogger("ytmp3-utils")

# Read cookies path
PATH = os.environ.get("COOKIES_PATH")
print(f"Getting cookies from: {PATH}")
print(f"File exists? {os.path.exists(PATH)}")
print(f"Readable? {os.access(PATH, os.R_OK)}")

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

    # --- yt-dlp config ---
        ydl_opts = {
        # --- Format selection ---
        "format": "bestaudio[ext=m4a]/bestaudio/best",  # prefers m4a > fallback to any audio
        "outtmpl": output_path,
        "cookiefile": PATH,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "prefer_ffmpeg": True,
        "nocheckcertificate": True,
        "socket_timeout": 30,
        "cachedir": False,
        "retries": 3,

        # --- Extraction stability ---
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android", "tv"],  # fallback across multiple clients
            }
        },

        # --- Post-processing chain ---
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            
        ],
    }


    try:
        logger.info(f"Starting download for: {url}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        # Verify output
        if not os.path.exists(final_mp3_path):
            # Handle common case: yt-dlp outputs .m4a first
            alt_path = os.path.join(TEMP_DIR, f"{video_id}.m4a")
            if os.path.exists(alt_path):
                os.rename(alt_path, final_mp3_path)
                logger.info("Renamed .m4a to .mp3 after conversion.")
            else:
                raise RuntimeError("Conversion failed: MP3 file was not created.")

        logger.info(f"Successfully converted: {final_mp3_path}")
        return final_mp3_path, os.path.basename(final_mp3_path)

    except yt_dlp.utils.DownloadError as de:
        logger.warning(f"Download error: {de}")
        raise RuntimeError(
            "The video is unavailable, private, age-restricted, or region-locked."
        ) from de

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error: {e}")

def cleanup_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up temp file: {path}")
    except Exception as e:
        logger.error(f"Cleanup failed for {path}: {e}")
