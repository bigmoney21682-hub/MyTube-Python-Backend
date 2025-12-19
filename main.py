# File: /main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

# --------------------------------------------------
# CORS (required for GitHub Pages frontend)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, "cookies.txt")

# --------------------------------------------------
# Health check
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# --------------------------------------------------
# TRENDING (RESTORED — SAFE, NO COOKIES)
# --------------------------------------------------
@app.get("/trending")
def trending(region: str = "US"):
    """
    Returns trending-style videos using a curated playlist.
    Does NOT require cookies.
    Keeps Home.jsx working.
    """

    PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLFgquLnL59amEA43C0R3G1-7x9X4XxkC8"

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        PLAYLIST_URL,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    data = json.loads(result.stdout)

    videos = []
    for e in data.get("entries", []):
        videos.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "uploaderName": e.get("uploader"),
            "thumbnail": f"https://i.ytimg.com/vi/{e.get('id')}/hqdefault.jpg",
            "views": None,
            "duration": None,
        })

    return videos

# --------------------------------------------------
# STREAMS (yt-dlp + cookies)
# --------------------------------------------------
@app.get("/streams/{video_id}")
def get_streams(video_id: str):
    """
    Returns playable stream data for a YouTube video.
    Uses yt-dlp with cookies.txt to bypass bot checks.
    """

    if not os.path.exists(COOKIES_PATH):
        raise HTTPException(
            status_code=500,
            detail="cookies.txt not found in backend root"
        )

    cmd = [
        "yt-dlp",
        "--cookies", COOKIES_PATH,
        "--no-playlist",
        "--dump-single-json",
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"yt-dlp error: {result.stderr.strip()}"
        )

    data = json.loads(result.stdout)

    video_streams = []
    audio_streams = []

    for f in data.get("formats", []):
        if f.get("vcodec") != "none":
            video_streams.append({
                "url": f.get("url"),
                "mimeType": f.get("ext"),
                "height": f.get("height"),
                "fps": f.get("fps"),
            })
        elif f.get("acodec") != "none":
            audio_streams.append({
                "url": f.get("url"),
                "mimeType": f.get("ext"),
                "abr": f.get("abr"),
            })

    return {
        "id": video_id,
        "title": data.get("title"),
        "uploader": data.get("uploader"),
        "videoStreams": video_streams,
        "audioStreams": audio_streams,
    }
