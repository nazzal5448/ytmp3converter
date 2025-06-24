from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import download_and_convert, cleanup_file
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-mp3-api")

# CORS config — update this in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain for security
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
        logger.info(f"Received request to convert URL: {url}")
        
        mp3_path, filename = await download_and_convert(url)

        # Schedule cleanup
        background_tasks.add_task(cleanup_file, mp3_path)

        return FileResponse(
            path=mp3_path,
            filename=filename,
            media_type="audio/mpeg"
        )

    except ValueError as ve:
        logger.warning(f"Bad request: {ve}")
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": str(ve)}
        )
    except Exception as e:
        logger.error(f"Internal error: {e}", exc_info=True)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error"}
        )
