# File: main.py
# Path: / (root of backend project)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
from fastapi.responses import JSONResponse

app = FastAPI(title="MyTube Backend")

# -----------------------
# CORS Configuration
# -----------------------
origins = [
    "https://bigmoney21682-hub.github.io",  # Your frontend URL
    "http://localhost:5173",                # Optional local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Routes
# -----------------------
@app.get("/trending")
async def trending(region: str = "US"):
    """
    Fetch trending videos for a given region.
    Returns JSON usable by the frontend.
    """
    try:
        ydl_opts = {
            "extract_flat": True,  # Only metadata, no video download
            "skip_download": True,
            "quiet": True,         # Hide verbose yt-dlp logs
        }

        search_str = f"ytsearchdate{region}:trending"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_str, download=False)

        return JSONResponse(content=info)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# -----------------------
# Health check
# -----------------------
@app.get("/")
async def root():
    return {"status": "MyTube Backend is running"}
