# File: backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

# CORS (frontend safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Absolute-safe cookie path
COOKIE_FILE = os.path.join(os.getcwd(), "cookies.txt")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/streams/{video_id}")
def get_streams(video_id: str):
    if not os.path.exists(COOKIE_FILE):
        raise HTTPException(status_code=500, detail="cookies.txt not found")

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "cookiefile": COOKIE_FILE,
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])

        streams = []
        for f in formats:
            if f.get("url") and f.get("vcodec") != "none":
                streams.append({
                    "url": f["url"],
                    "mimeType": f.get("ext"),
                    "quality": f.get("height"),
                })

        return {
            "id": video_id,
            "title": info.get("title"),
            "streams": streams,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
