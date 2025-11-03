import os
import logging
import aiohttp
from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Initialize FastAPI app
app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-mp3-api")

# CORS setup (change domain before going to production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youtubemp3converter.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "YouTube MP3 Converter API is running."}


@app.post("/convert")
async def convert_youtube_video(url: str = Form(...)):
    """
    Converts YouTube video to MP3 via RapidAPI
    """
    try:
        logger.info(f"Conversion started for: {url}")

        api_url = "https://yt-search-and-download-mp3.p.rapidapi.com/mp3"
        params = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers, params=params) as response:
                data = await response.json()

        if not data.get("success"):
            raise RuntimeError(f"API returned an error: {data}")

        download_url = data.get("download")
        title = data.get("title", "output")

        if not download_url:
            raise ValueError("Download URL missing in API response")

        logger.info(f"Conversion successful for '{title}'")

        # Redirect user to the RapidAPI download link
        return RedirectResponse(url=download_url)

    except ValueError as ve:
        logger.warning(f"Client error: {ve}")
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": str(ve)}
        )

    except RuntimeError as re:
        logger.warning(f"Download error: {re}")
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": str(re)}
        )

    except Exception as e:
        logger.error(f"Server crash: {e}", exc_info=True)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Unexpected server error. Please try again later."}
        )
