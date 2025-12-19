# File: main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="MyTube Python Backend")

# Allow all origins for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route for testing
@app.get("/")
async def root():
    return {"message": "MyTube backend is live!"}


# -----------------------------
# Helper function for yt-dlp
# -----------------------------
def ytdlp_extract_info(url: str, download: bool = False):
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": not download,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=download)
            return info
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# Search endpoint
# -----------------------------
@app.get("/search")
async def search(query: str = Query(..., description="Search query")):
    search_url = f"ytsearch10:{query}"  # top 10 results
    info = ytdlp_extract_info(search_url)
    results = []
    for entry in info.get("entries", []):
        results.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "url": entry.get("webpage_url"),
            "duration": entry.get("duration"),
            "thumbnail": entry.get("thumbnail")
        })
    return {"results": results}


# -----------------------------
# Video info endpoint
# -----------------------------
@app.get("/video")
async def video_info(url: str = Query(..., description="YouTube video URL")):
    info = ytdlp_extract_info(url)
    formats = []
    for f in info.get("formats", []):
        formats.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or f"{f.get('height')}p",
            "url": f.get("url"),
            "filesize": f.get("filesize")
        })
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "description": info.get("description"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "formats": formats
    }


# -----------------------------
# Playlist info endpoint
# -----------------------------
@app.get("/playlist")
async def playlist_info(url: str = Query(..., description="YouTube playlist URL")):
    info = ytdlp_extract_info(url)
    videos = []
    for entry in info.get("entries", []):
        videos.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "url": entry.get("webpage_url"),
            "duration": entry.get("duration"),
            "thumbnail": entry.get("thumbnail")
        })
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "url": info.get("webpage_url"),
        "videos": videos
    }
