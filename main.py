# File: main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import yt_dlp

app = FastAPI(title="MyTube Python Backend", version="1.0")

# ---------------------------
# CORS Configuration
# ---------------------------
allowed_origins = [
    "http://localhost:5173",  # local frontend
    "https://mytube-frontend.onrender.com",  # live frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Utility functions
# ---------------------------
def extract_video_info(url: str) -> Dict:
    """
    Extracts video information using yt-dlp.
    """
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "webpage_url": info.get("webpage_url"),
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/")
async def root():
    return {"message": "MyTube backend is live!"}

@app.get("/search")
async def search_videos(query: str):
    """
    Search YouTube for videos using yt-dlp.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "default_search": "ytsearch5",  # returns top 5 results
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(query, download=False)
            videos = []
            for entry in results.get("entries", []):
                videos.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                })
            return {"query": query, "results": videos}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/video/{video_id}")
async def get_video(video_id: str):
    """
    Get detailed video info by video ID.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    return extract_video_info(url)
