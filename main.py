from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Initialize FastAPI
app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-mp3-api")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youtubemp3converter.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "YouTube MP3 Converter API (RapidAPI Version) is running."}

@app.post("/convert")
async def convert_youtube_video(url: str = Form(...)):
    """Convert YouTube video to MP3 using RapidAPI."""
    logger.info(f"Conversion started for: {url}")

    try:
        endpoint = "https://yt-search-and-download-mp3.p.rapidapi.com/mp3"
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
        }
        params = {"url": url}

        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code != 200:
            logger.warning(f"RapidAPI error {response.status_code}: {response.text}")
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Failed to fetch MP3. Please try again."},
            )

        data = response.json()
        logger.info(f"Raw API Response: {data}")

        # Extract correct fields from API response
        title = data.get("title", "Unknown")
        download_url = data.get("download")
        duration = data.get("duration")
        file_type = data.get("type")
        size = data.get("size")

        if not download_url:
            logger.warning(f"No download URL found in API response: {data}")
            return JSONResponse(
                status_code=502,
                content={"error": "No download URL received from RapidAPI."},
            )

        logger.info(f"Conversion successful for: {title}")

        return {
            "success": True,
            "title": title,
            "type": file_type,
            "size": size,
            "download_url": download_url,
            "duration": duration,
        }

    except Exception as e:
        logger.error(f"Server crash: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected server error. Please try again later."},
        )
