# File: main.py
# Path: / (root of backend project)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import json
from typing import Optional

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- yt-dlp OPTIONS ----------------
YDL_OPTS = {
    "cookiefile": "cookies.txt",       # <-- Your cookies file in root
    "ignoreerrors": True,
    "quiet": True,
    "format": "bestvideo+bestaudio/best",
    "simulate": True,
    "nocheckcertificate": True,
    "extract_flat": "in_playlist",     # For trending/search lists
}

# ---------------- HELPER ----------------
def extract_info(url: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- ENDPOINTS ----------------
@app.get("/trending")
def trending(region: Optional[str] = "US"):
    """
    Returns trending videos. region param is optional (default US)
    """
    url = "https://www.youtube.com/feed/trending"
    try:
        info = extract_info(url)
        if not info:
            return []
        # yt-dlp returns dict with 'entries' for playlists/lists
        return info.get("entries", [])
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e.detail))

@app.get("/search")
def search(q: str):
    """
    Returns search results for query q
    """
    if not q:
        raise HTTPException(status_code=400, detail="Missing search query")

    url = f"ytsearch10:{q}"  # top 10 results
    try:
        info = extract_info(url)
        if not info:
            return []
        return info.get("entries", [])
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e.detail))

@app.get("/streams/{video_id}")
def streams(video_id: str):
    """
    Returns available streams for a given video
    """
    if not video_id:
        raise HTTPException(status_code=400, detail="Missing video ID")

    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        info = extract_info(url)
        if not info:
            return {
                "title": "Placeholder",
                "uploaderName": "Unknown",
                "views": 0,
                "videoStreams": [],
                "relatedStreams": [],
            }

        # Simplify streams for frontend consumption
        video_streams = []
        if "formats" in info:
            for f in info["formats"]:
                video_streams.append({
                    "url": f.get("url"),
                    "format": f.get("ext"),
                    "bitrate": f.get("tbr"),
                    "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                })

        related_streams = []
        for e in info.get("related", []):
            related_streams.append({
                "title": e.get("title"),
                "url": f"https://www.youtube.com/watch?v={e.get('id')}" if e.get("id") else None,
                "thumbnail": e.get("thumbnails")[0]["url"] if e.get("thumbnails") else None,
                "uploaderName": e.get("uploader"),
                "views": e.get("view_count"),
                "duration": e.get("duration"),
                "type": "stream",
            })

        return {
            "title": info.get("title", "Placeholder"),
            "uploaderName": info.get("uploader", "Unknown"),
            "views": info.get("view_count", 0),
            "videoStreams": video_streams,
            "relatedStreams": related_streams,
        }

    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e.detail))
