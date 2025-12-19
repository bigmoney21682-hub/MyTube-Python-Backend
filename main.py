# File: /main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

# --------------------------------------------------
# CORS
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
# TRENDING (curated, stable playlist)
# --------------------------------------------------
@app.get("/trending")
def trending():
    PLAYLIST_URL = (
        "https://www.youtube.com/playlist"
        "?list=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-"
    )

    cmd = [
        "yt-dlp",
        "--cookies", COOKIES_PATH,
        "--dump-single-json",
        "--flat-playlist",
        PLAYLIST_URL,
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
            detail=result.stderr.strip()
        )

    data = json.loads(result.stdout)

    videos = []
    for entry in data.get("entries", []):
        videos.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "author": entry.get("uploader"),
            "thumbnail": f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
        })

    return videos

# --------------------------------------------------
# STREAMS (unchanged, working)
# --------------------------------------------------
@app.get("/streams/{video_id}")
def get_streams(video_id: str):

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
            detail=result.stderr.strip()
        )

    data = json.loads(result.stdout)

    formats = data.get("formats", [])
    video_streams = []
    audio_streams = []

    for f in formats:
        if f.get("vcodec") != "none":
            video_streams.append({
                "url": f.get("url"),
                "mimeType": f.get("ext"),
                "height": f.get("height"),
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
