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
        "--cookies", COOKIES_PATH,          # 🔑 THIS IS THE FIX
        "--no-playlist",
        "--dump-single-json",
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"yt-dlp error: {result.stderr.strip()}"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse yt-dlp output"
        )

    # Extract usable streams
    formats = data.get("formats", [])

    video_streams = []
    audio_streams = []

    for f in formats:
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
