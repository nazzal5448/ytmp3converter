from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import download_and_convert, cleanup_file
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import logging

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-mp3-api")

# CORS setup — update origins before going to production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youtubemp3converter.net/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "YouTube MP3 Converter API is running."}

@app.post("/convert")
async def convert_youtube_video(
    url: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    try:
        logger.info(f"Conversion started for: {url}")
        mp3_path, filename = await download_and_convert(url)
        background_tasks.add_task(cleanup_file, mp3_path)

        logger.info(f"Conversion successful: {filename}")
        return FileResponse(
            path=mp3_path,
            filename=filename,
            media_type="audio/mpeg"
        )

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
