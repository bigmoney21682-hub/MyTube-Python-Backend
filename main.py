# File: main.py
# Path: / (root of backend project)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL
import re

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost:5173",
    "*",  # allow all for now; you can restrict later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- YT-DLP OPTIONS ----------------
ydl_opts_extract = {
    "quiet": True,
    "extract_flat": True,  # Only metadata, no downloads
    "skip_download": True,
}

ydl_opts_full = {
    "quiet": True,
}

# ---------------- TRENDING ----------------
TRENDING_PLAYLIST = "PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"  # Example curated playlist

@app.get("/trending")
def trending():
    """Return curated playlist videos as trending."""
    try:
        with YoutubeDL(ydl_opts_extract) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/playlist?list={TRENDING_PLAYLIST}", download=False)
            videos = info.get("entries", [])
            result = []
            for v in videos:
                result.append({
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "uploaderName": v.get("uploader"),
                    "thumbnail": v.get("thumbnail"),
                    "views": v.get("view_count", 0),
                    "duration": v.get("duration"),
                })
            return result
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

# ---------------- SEARCH ----------------
@app.get("/search")
def search(q: str):
    """Search YouTube videos using yt-dlp."""
    if not q.strip():
        return []

    try:
        with YoutubeDL(ydl_opts_extract) as ydl:
            info = ydl.extract_info(f"ytsearch10:{q}", download=False)
            videos = info.get("entries", [])
            result = []
            for v in videos:
                result.append({
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "uploaderName": v.get("uploader"),
                    "thumbnail": v.get("thumbnail"),
                    "views": v.get("view_count", 0),
                    "duration": v.get("duration"),
                })
            return result
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

# ---------------- STREAMS ----------------
@app.get("/streams/{video_id}")
def streams(video_id: str):
    """Return stream URLs for a specific video."""
    try:
        with YoutubeDL(ydl_opts_full) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

            video_streams = []
            if "formats" in info:
                for f in info["formats"]:
                    video_streams.append({
                        "format": f.get("ext"),
                        "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                        "url": f.get("url"),
                        "bitrate": f.get("tbr", 0),
                        "resolution": f.get("resolution") or f"{f.get('height', 0)}p"
                    })

            related_streams = []
            for r in info.get("related_videos", []):
                related_streams.append({
                    "type": "stream",
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "url": f"https://www.youtube.com/watch?v={r.get('id')}",
                    "thumbnail": r.get("thumbnail"),
                    "uploaderName": r.get("uploader"),
                    "views": r.get("view_count"),
                    "duration": r.get("duration"),
                })

            response = {
                "title": info.get("title", "Placeholder"),
                "uploaderName": info.get("uploader", "Unknown"),
                "views": info.get("view_count", 0),
                "videoStreams": video_streams,
                "relatedStreams": related_streams,
                "hls": info.get("url") if info.get("url", "").endswith(".m3u8") else None,
            }

            return response

    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)
