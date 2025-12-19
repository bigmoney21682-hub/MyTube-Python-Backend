# File: main.py
# Path: / (root of your backend project)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="MyTube Backend")

# ----------------------------
# CORS Configuration
# ----------------------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost:5173"  # Optional: for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Models
# ----------------------------
class VideoRequest(BaseModel):
    url: str

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
async def root():
    return {"message": "Welcome to MyTube Backend!"}


@app.post("/download/")
async def download_video(request: VideoRequest):
    try:
        ydl_opts = {
            "format": "best",
            "noplaylist": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
        return {
            "title": info.get("title"),
            "id": info.get("id"),
            "url": info.get("webpage_url"),
            "duration": info.get("duration")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health/")
async def health_check():
    return {"status": "ok"}
